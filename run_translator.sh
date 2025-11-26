#!/bin/bash
# Скрипт для запуска переводчика
# Использование: ./run_translator.sh "Input/файл.docx"

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем переводчик с переданными параметрами
python3 main.py "$@"

