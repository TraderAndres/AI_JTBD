# config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ensure this environment variable is set
# MODEL_NAME = "gpt-4"
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.5
MAX_TOKENS = 3000
