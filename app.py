from flask import Flask, render_template, request, jsonify
from rapidfuzz import process
import base64
import whisper
import tempfile
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
import uuid
from clients import KalshiHttpClient, KalshiWebSocketClient, Environment
import os
import json
from datetime import datetime, timezone
from openai import OpenAI
from config import (
    OPENAI_API_KEY, 
    DEFAULT_MODEL, 
    MAX_TOKENS, 
    TEMPERATURE, 
    SYSTEM_PROMPT,
    CATEGORY_PROMPT,
    EVENTS_PROMPT,
    CATEGORIES,
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG
)
import requests

app = Flask(__name__)

# Load environment variables first
load_dotenv()
env = Environment.DEMO # toggle environment here
KEYID = os.getenv('DEMO_KEYID') if env == Environment.DEMO else os.getenv('PROD_KEYID')
KEYFILE = os.getenv('DEMO_KEYFILE') if env == Environment.DEMO else os.getenv('PROD_KEYFILE')

# Initialize OpenAI client
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found. Please set it in your environment or .env file.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

# Store conversation history (in a real app, you'd use a database)
url = "https://api.elections.kalshi.com/trade-api/v2/markets"
response = requests.get(url)
markets_data = response.json()
conversations = {}

model = whisper.load_model("turbo")

try:
    with open(KEYFILE, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
except FileNotFoundError:
    raise FileNotFoundError(f"Private key file not found at {KEYFILE}")
except Exception as e:
    raise Exception(f"Error loading private key: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    conversation_id = data.get('conversation_id', 'default')
    
    # Initialize conversation if it doesn't exist
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Add user message to conversation
    user_message = {
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id].append(user_message)
    
    # Call OpenAI API if available
    if client:
        try:            
            ai_response = get_response(message)
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            ai_response = f"I received your message: '{message}'. This is where your logic would go. (Note: OpenAI API call failed - {str(e)})"
    else:
        ai_response = f"I received your message: '{message}'. This is where your logic would go. (Note: OpenAI API key not configured)"
    
    # Add assistant response to conversation
    assistant_message = {
        'role': 'assistant',
        'content': ai_response,
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id].append(assistant_message)
    
    return jsonify({
        'response': ai_response,
        'conversation_id': conversation_id
    })

@app.route('/api/audio', methods=['POST'])
def audio():
    # Handle audio file upload
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    
    audio_file = request.files['audio']
    conversation_id = request.form.get('conversation_id', 'default')
    
    # Add to conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    try:
        file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else '.wav'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        result = model.transcribe(temp_file_path)
        transcribed_text = result["text"]
        user_message = {
            'role': 'user',
            'content': transcribed_text,
            'timestamp': datetime.now().isoformat()
        }
        conversations[conversation_id].append(user_message)
        response = get_response(transcribed_text)

        # Clean up the temporary file
        os.unlink(temp_file_path)

    except Exception as e:
        print(f"Audio transcription error: {e}")
        response = f"Sorry, I couldn't transcribe your audio message. Error: {str(e)}"

    assistant_message = {
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id].append(assistant_message)
    
    return jsonify({
        'transcribed_text': transcribed_text,
        'response': response,
        'conversation_id': conversation_id
    })

def shortlist_series(series, msg):
    scored = []
    for s in series:
        title = s[1].lower()
        tags  = " ".join(s[2]).lower() if s[2] else ""
        # score = process.extractOne(msg, [title + " " + tags])[1]
        score = sum(t in msg for t in title.lower().split()) + sum(t in msg for t in tags.lower().split())
        scored.append((score, s))
    scored.sort(reverse=True, key=lambda x: x[0])
    scored = scored[:min(len(scored), 25)]
    scored = [x[1] for x in scored]
    return scored

def sign_request(private_key, timestamp, method, path):
    # Create the message to sign
    message = f"{timestamp}{method}{path}".encode('utf-8')
    
    # Sign with RSA-PSS
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Return base64 encoded
    return base64.b64encode(signature).decode('utf-8')

def get_response(message):
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": CATEGORY_PROMPT + ", ".join(CATEGORIES)},
            {"role": "user", "content": message}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    key_words = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "Extract the key words from the user's input and return them in lowercase as a comma separated list."},
            {"role": "user", "content": message}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )

    key_words = set(key_words.choices[0].message.content.split(", "))
    
    # Extract the response content
    categories = response.choices[0].message.content.split(", ")

    series = []
    for category in categories:
        s = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/series?category={category}")
        data = s.json()
        if data["series"]:
            series += [[item["ticker"], item["title"], item["tags"]] for item in data["series"]]

    shortlisted_series = shortlist_series(series, key_words)
    events = []
    for ticker, _, _ in shortlisted_series:
        e = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/events?series_ticker={ticker}&min_close_ts=1")
        data = e.json()
        for item in data["events"]:
            events.append([item["title"], item["event_ticker"]])

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": EVENTS_PROMPT},
            {"role": "system", "content": json.dumps(events)},
            {"role": "user", "content": message}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0
    )
    
    best_ticker = response.choices[0].message.content

    market_ticker = None
    m = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker={best_ticker}")
    data = m.json()
    for item in data["markets"]:
        open_time = datetime.fromisoformat(item["open_time"].replace("Z", "+00:00"))
        close_time = datetime.fromisoformat(item["close_time"].replace("Z", "+00:00"))
        if open_time < datetime.now(timezone.utc) < close_time:
            market_ticker = item["ticker"]
            break

    if market_ticker != None:
        timestamp = str(int(datetime.now(timezone.utc).timestamp() * 1000))
        method = "POST"
        path = "/trade-api/v2/portfolio/orders"
        signature = sign_request(private_key, timestamp, method, path)

        headers = {
            'KALSHI-ACCESS-KEY': KEYID,
            'KALSHI-ACCESS-SIGNATURE': signature,
            'KALSHI-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }

        order_data = {
            "ticker": market_ticker,
            "action": "buy",
            "side": "yes",
            "count": 1,
            "type": "limit",
            "yes_price": 99,
            "client_order_id": str(uuid.uuid4())
        }
        print(market_ticker)
        response = requests.post("https://demo-api.kalshi.co/trade-api/v2/portfolio/orders", headers=headers, json=order_data)
        if response.status_code == 201:
            order = response.json()['order']
            ai_response = f"Order placed successfully! Order ID: {order['order_id']} Client Order ID: {order_data['client_order_id']} Status: {order['status']}"

        else:
            ai_response = f"Error: {response.status_code} - {response.text}"
    else:
        ai_response = "Currently no markets found for this trade."
    
    return ai_response

@app.route('/api/conversations/<conversation_id>')
def get_conversation(conversation_id):
    return jsonify(conversations.get(conversation_id, []))

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)