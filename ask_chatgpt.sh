#!/bin/bash
# Простой скрипт для запроса рекомендаций у ChatGPT

cd "$(dirname "$0")"
source venv/bin/activate

# Проверяем аргументы
if [ "$1" == "--analyze" ]; then
    FILE="$2"
    QUESTION="$3"
    python3 chatgpt_agent.py --analyze "$FILE" "$QUESTION"
elif [ "$1" == "--show" ]; then
    python3 chatgpt_agent.py --show
else
    echo "🤖 ChatGPT Agent - Простой интерфейс"
    echo ""
    echo "Использование:"
    echo "  ./ask_chatgpt.sh --analyze [файл] [вопрос]"
    echo "  ./ask_chatgpt.sh --show"
    echo ""
    echo "Примеры:"
    echo "  ./ask_chatgpt.sh --analyze translator.py 'Как улучшить обработку ошибок?'"
    echo "  ./ask_chatgpt.sh --analyze '' 'Проанализируй весь проект'"
    echo "  ./ask_chatgpt.sh --show"
    echo ""
    # Интерактивный режим
    python3 chatgpt_agent.py
fi

