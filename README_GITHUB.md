# 📚 AI-Powered Book Translator (RU → EN)

Automated translation system for Russian fiction books to American English using Machine Translation (MT) + LLM post-editing.

## 🎯 Features

- **Multiple MT Systems**: DeepL, Google Translate, Yandex Translate
- **LLM Post-Editing**: GPT-4, Claude 3.5 Sonnet, DeepSeek, Grok, Crok
- **Glossary Management**: Ensures consistency of names, terms, and phrases
- **Translation Memory**: Reuses previous translations for consistency
- **DOCX Support**: Reads and writes Word documents preserving structure
- **Two-Stage Process**: MT → LLM post-editing for natural, human-like translation

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/book-translator.git
cd book-translator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env_template.txt .env
# Edit .env and add your API keys
```

### Basic Usage

```bash
# Translate a document
python main.py "Input/book.docx"

# Specify MT engine and LLM editor
python main.py "Input/book.docx" --mt-engine deepl --llm-editor gpt4

# Use Translation Memory
python main.py "Input/book.docx" --use-tm
```

## 📖 Documentation

- **[ALGORITHM.md](ALGORITHM.md)** - Detailed algorithm description
- **[API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)** - How to get API keys
- **[GLOSSARY_GUIDE.md](GLOSSARY_GUIDE.md)** - Glossary management guide
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - GitHub repository setup

## 🔧 Architecture

```
Input (.docx) → MT (DeepL) → Glossary → LLM Post-Edit → Output (.docx)
                ↓
         Translation Memory
```

## 📋 Requirements

- Python 3.8+
- API keys for:
  - At least one MT system (DeepL recommended)
  - At least one LLM (GPT-4 recommended)

## 🛠️ Components

- `translator.py` - Main translation orchestrator
- `mt_engines.py` - MT system implementations
- `llm_post_editor.py` - LLM post-editing implementations
- `glossary.py` - Glossary management
- `translation_memory.py` - Translation Memory system
- `docx_handler.py` - DOCX file handling

## 📝 License

[Add your license here]

## 🤝 Contributing

This is a personal project for translating fiction books. Feel free to fork and adapt for your needs.

## ⚠️ Security Note

Never commit `.env` file with API keys. It's already in `.gitignore` for your safety.

