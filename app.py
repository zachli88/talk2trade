from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime, timezone
from openai import OpenAI
from config import (
    OPENAI_API_KEY, 
    DEFAULT_MODEL, 
    MAX_TOKENS, 
    TEMPERATURE, 
    SYSTEM_PROMPT,
    CATEGORY_PROMPT,
    CATEGORIES,
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG
)
import requests

app = Flask(__name__)

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
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": CATEGORY_PROMPT + ", ".join(CATEGORIES)},
                    {"role": "user", "content": message}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            # Extract the response content
            ai_response = response.choices[0].message.content
            categories = ai_response.split(", ")

            series_tickers = []
            for category in categories:
                s = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/series?category={category}")
                data = s.json()
                tickers = [item["ticker"] for item in data["series"]]
                series_tickers += tickers
            markets = []
            for ticker in series_tickers:
                m = requests.get(f"https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker={ticker}")
                data = m.json()
                for item in data["markets"]:
                    open_time = datetime.fromisoformat(item["open_time"].replace("Z", "+00:00"))
                    close_time = datetime.fromisoformat(item["close_time"].replace("Z", "+00:00"))
                    if open_time < datetime.now(timezone.utc) < close_time:
                        markets.append(item)
            
            print(markets)
            
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
    
    # Here you would process the audio file
    # For now, we'll just acknowledge receipt
    response = "I received your audio message. Audio processing would happen here."
    
    # Add to conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    user_message = {
        'role': 'user',
        'content': '[Audio Message]',
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id].append(user_message)
    
    assistant_message = {
        'role': 'assistant',
        'content': response,
        'timestamp': datetime.now().isoformat()
    }
    conversations[conversation_id].append(assistant_message)
    
    return jsonify({
        'response': response,
        'conversation_id': conversation_id
    })

@app.route('/api/conversations/<conversation_id>')
def get_conversation(conversation_id):
    return jsonify(conversations.get(conversation_id, []))

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)