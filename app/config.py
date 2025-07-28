# config.py
from dotenv import load_dotenv
import os
import pathlib

BASE_PATH = pathlib.Path(__file__).parent

load_dotenv()

# backend API details
PROMPT_FILE = BASE_PATH / "prompts/prototype_base_system_prompt.txt"
PROMPT_FILE = str(PROMPT_FILE)

# load prompt
with open(PROMPT_FILE, 'r') as file:
    SYSTEM_PROMPT = file.read()

# LLM API Details
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL")
CLAUDE_API_ROUTE = os.getenv("CLAUDE_API_ROUTE")
MAX_TOKENS = 1024
ANTHROPIC_VERSION = "2023-06-01"
