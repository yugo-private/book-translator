# Переводчик художественных текстов (RU → EN)

Система автоматического перевода художественных книг с русского на английский язык с использованием комбинации машинного перевода (MT) и пост-редактирования через LLM.

## Возможности

- **Множественные MT системы**: DeepL, Google Translate, Yandex Translate
- **LLM пост-редактирование**: GPT-4, Claude 3.5 Sonnet, DeepSeek, Crok, Grok
- **Глоссарий**: Обеспечивает консистентность перевода имен, терминов и фраз
- **Translation Memory**: Сохранение и повторное использование переводов для консистентности
- **Работа с .docx**: Чтение и запись Word документов с сохранением структуры
- **Двухэтапный процесс**: MT → LLM пост-редактирование для максимально естественного перевода

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example` и добавьте ваши API ключи:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваши API ключи
```

## Использование

### Базовое использование

```bash
python main.py "Input/Pintek ch1 RU.docx"
```

### С указанием MT движка и LLM редактора

```bash
python main.py "Input/Pintek ch1 RU.docx" --mt-engine deepl --llm-editor gpt4
```

### С указанием выходного файла

```bash
python main.py "Input/Pintek ch1 RU.docx" -o "Output/Pintek_ch1_EN.docx"
```

### Без использования глоссария

```bash
python main.py "Input/Pintek ch1 RU.docx" --no-glossary
```

### С использованием Translation Memory

```bash
python main.py "Input/Pintek ch1 RU.docx" --use-tm
```

### Параметры

- `input_file` - Путь к входному .docx файлу (обязательный)
- `-o, --output` - Путь к выходному файлу (опционально)
- `--mt-engine` - MT движок: `deepl`, `google`, `yandex` (по умолчанию из config)
- `--llm-editor` - LLM редактор: `gpt4`, `claude`, `deepseek`, `crok` (по умолчанию из config)
- `--batch-size` - Количество параграфов для обработки за раз (по умолчанию: 5)
- `--no-glossary` - Не использовать глоссарий
- `--use-tm` - Использовать Translation Memory для повторного использования переводов

## Глоссарий и Translation Memory

### Глоссарий

Глоссарий хранится в файле `glossary.json` и используется для обеспечения консистентности перевода. Вы можете редактировать его вручную или использовать утилиту `manage_glossary.py`.

### Управление глоссарием через командную строку:

```bash
# Добавить запись
python manage_glossary.py add "Артём" "Artyom"

# Показать все записи
python manage_glossary.py list

# Удалить запись
python manage_glossary.py remove "Артём"

# Импортировать из JSON файла
python manage_glossary.py import my_glossary.json

# Экспортировать в JSON файл
python manage_glossary.py export backup_glossary.json
```

### Пример структуры `glossary.json`:
```json
{
  "Пинтек": "Pintek",
  "Артём": "Artyom",
  "Катя": "Katya",
  "Глубинка": "Hinterland"
}
```

### Translation Memory

Translation Memory (TM) сохраняет ранее переведенные сегменты текста и автоматически использует их при повторении похожих фраз. Это особенно полезно:

- При переводе серии книг
- Для повторяющихся описаний и фраз
- Экономии на API вызовах
- Обеспечения консистентности перевода

TM включается флагом `--use-tm` и автоматически сохраняет все переводы в файл `translation_memory.json`.

## Рекомендации по использованию

### Для лучшего качества перевода:

1. **MT движок**: Рекомендуется использовать **DeepL** для лучшего качества базового перевода
2. **LLM редактор**: Рекомендуется **GPT-4** или **Claude 3.5 Sonnet** для пост-редактирования
3. **Глоссарий**: Обязательно создайте глоссарий с именами персонажей и ключевыми терминами перед началом перевода
4. **Батчинг**: Используйте `--batch-size 3-5` для баланса между качеством и скоростью

### Процесс работы:

1. Подготовьте глоссарий с именами персонажей и ключевыми терминами
2. Запустите перевод с выбранными MT и LLM системами
3. Проверьте результат и при необходимости добавьте записи в глоссарий
4. Повторите перевод для улучшения консистентности

## Структура проекта

```
Translate/
├── Input/              # Входные файлы
├── Output/             # Выходные файлы
├── config.py           # Конфигурация
├── translator.py       # Основной класс переводчика
├── mt_engines.py       # MT системы
├── llm_post_editor.py  # LLM пост-редактирование
├── glossary.py         # Управление глоссарием
├── translation_memory.py  # Translation Memory для повторного использования переводов
├── docx_handler.py     # Работа с .docx файлами
├── main.py             # Точка входа
├── manage_glossary.py  # Утилита управления глоссарием
├── example_usage.py    # Примеры использования
├── glossary.json       # Глоссарий (создается автоматически)
├── translation_memory.json  # Translation Memory (создается автоматически при --use-tm)
├── .env                # API ключи (создайте на основе .env.example)
└── requirements.txt    # Зависимости
```

## API ключи

### Где получить API ключи:

- **DeepL**: https://www.deepl.com/pro-api
- **Google Translate**: https://cloud.google.com/translate/docs/setup
- **Yandex Translate**: https://yandex.com/dev/translate/
- **OpenAI (GPT-4)**: https://platform.openai.com/api-keys
- **Anthropic (Claude)**: https://console.anthropic.com/
- **DeepSeek**: https://platform.deepseek.com/
- **Crok**: Проверьте документацию Crok API
- **Grok (xAI)**: https://console.x.ai/

## Примеры использования

### Перевод первой главы с DeepL + GPT-4:

```bash
python main.py "Input/Pintek ch1 RU.docx" --mt-engine deepl --llm-editor gpt4
```

### Перевод с Claude для пост-редактирования:

```bash
python main.py "Input/Pintek ch1 RU.docx" --mt-engine deepl --llm-editor claude
```

### Перевод с DeepSeek (более экономичный вариант):

```bash
python main.py "Input/Pintek ch1 RU.docx" --mt-engine deepl --llm-editor deepseek
```

### Перевод с Grok:

```bash
python main.py "Input/Pintek ch1 RU.docx" --mt-engine deepl --llm-editor grok
```

## Примечания

- Переводчик обрабатывает документы по параграфам для оптимизации работы с API
- Промежуточные результаты MT перевода не сохраняются (только финальный результат после LLM пост-редактирования)
- Глоссарий применяется автоматически к переводу для обеспечения консистентности
- Для больших документов процесс может занять значительное время из-за двухэтапной обработки

## Лицензия

Проект для личного использования.

