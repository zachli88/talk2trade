import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Model Configuration
DEFAULT_MODEL = "gpt-4"  # Change to "gpt-4" if you have access
MAX_TOKENS = 500
TEMPERATURE = 0.7

CATEGORIES = ["COVID-19", "Climate and Weather", "Companies", "Crypto", "Economics", "Elections", "Education", "Entertainment", "Financials", "Health", "Mentions", "Politics", "Science and Technology", "Sports", "Social", "Transportation", "World"]

CATEGORY_PROMPT = """You are Talk2Trade, an AI-powered trading assistant for the Kalshi platform. 
Here is a list of categories that are currently available on the platform. The user's input is a trade they want to make on Kalshi.
Use this list to return only the most relevant category(ies) for the user's input. Categories: """

EVENTS_PROMPT = """Choose the single best event that is most relevant to the user's input based on titles. 
The user's input is a trade they want to make on Kalshi. Return ONLY the ticker as plain text (no quotes, no JSON, no code blocks)."""

# System Prompt for Talk2Trade
SYSTEM_PROMPT = """You are Talk2Trade, an AI-powered trading assistant. Help users with:

- Trading questions and strategies
- Market analysis and insights
- Investment advice and portfolio management
- Risk management and position sizing
- Understanding financial instruments
- Market trends and economic indicators

Be helpful, informative, and professional. Always remind users that this is not financial advice and they should do their own research and consult with financial professionals.

Keep responses concise but informative, typically under 200 words unless more detail is specifically requested."""

# Kalshi API Configuration
KALSHI_ENVIRONMENT = os.getenv('KALSHI_ENVIRONMENT', 'demo')  # 'demo' or 'prod'
KALSHI_DEMO_KEYID = os.getenv('DEMO_KEYID')
KALSHI_DEMO_KEYFILE = os.getenv('DEMO_KEYFILE')
KALSHI_PROD_KEYID = os.getenv('PROD_KEYID')
KALSHI_PROD_KEYFILE = os.getenv('PROD_KEYFILE')

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True
