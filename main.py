"""
Главный скрипт для запуска переводчика.
"""

import argparse
import os
from translator import Translator
from config import INPUT_DIR, OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(
        description="Переводчик художественных текстов с русского на английский (MT + LLM пост-редактирование)"
    )
    
    parser.add_argument(
        "input_file",
        help="Путь к входному .docx файлу (относительно Input/ или абсолютный)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Путь к выходному файлу (по умолчанию: Output/<имя_файла>_EN.docx)"
    )
    
    parser.add_argument(
        "--mt-engine",
        choices=["deepl", "google", "yandex"],
        default=None,
        help="MT движок для перевода (по умолчанию из config)"
    )
    
    parser.add_argument(
        "--llm-editor",
        choices=["gpt4", "claude", "deepseek", "crok", "grok"],
        default=None,
        help="LLM редактор для пост-редактирования (по умолчанию из config)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Количество параграфов для обработки за раз (по умолчанию: 5)"
    )
    
    parser.add_argument(
        "--no-glossary",
        action="store_true",
        help="Не использовать глоссарий"
    )
    
    parser.add_argument(
        "--use-tm",
        action="store_true",
        help="Использовать Translation Memory для повторного использования переводов"
    )
    
    args = parser.parse_args()
    
    # Определяем пути к файлам
    if os.path.isabs(args.input_file):
        input_path = args.input_file
    else:
        input_path = os.path.join(INPUT_DIR, args.input_file)
    
    if not os.path.exists(input_path):
        print(f"Ошибка: файл не найден: {input_path}")
        return
    
    if args.output:
        output_path = args.output
    else:
        # Генерируем имя выходного файла
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}_EN.docx")
    
    # Создаем переводчик
    try:
        translator = Translator(
            mt_engine=args.mt_engine, 
            llm_editor=args.llm_editor,
            use_tm=args.use_tm
        )
    except Exception as e:
        print(f"Ошибка инициализации переводчика: {e}")
        print("\nУбедитесь, что:")
        print("1. Все необходимые API ключи указаны в файле .env")
        print("2. Установлены все зависимости: pip install -r requirements.txt")
        return
    
    # Выполняем перевод
    try:
        translator.translate_docx(
            input_path=input_path,
            output_path=output_path,
            batch_size=args.batch_size,
            use_glossary=not args.no_glossary
        )
        print(f"\n✓ Перевод сохранен в: {output_path}")
    except Exception as e:
        print(f"\n✗ Ошибка при переводе: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

