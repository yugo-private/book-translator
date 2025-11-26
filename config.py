"""
Конфигурационный файл для агента-переводчика.
Создайте файл .env в корне проекта и добавьте туда ваши API ключи.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# MT Systems API Keys
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")

# LLM API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
CROK_API_KEY = os.getenv("CROK_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# Настройки перевода
DEFAULT_MT_ENGINE = os.getenv("DEFAULT_MT_ENGINE", "deepl")  # deepl, google, yandex
DEFAULT_LLM_ENGINE = os.getenv("DEFAULT_LLM_ENGINE", "gpt4")  # gpt4, claude, deepseek, crok, grok

# Настройки LLM
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))

# Пути
INPUT_DIR = "Input"
OUTPUT_DIR = "Output"
GLOSSARY_FILE = "glossary.json"

