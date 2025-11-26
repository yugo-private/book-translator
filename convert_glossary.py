"""
Утилита для конвертации глоссария из формата ChatGPT в формат системы.
"""

import json
import sys
import os


def convert_chatgpt_glossary(input_file: str, output_file: str = "glossary.json"):
    """
    Конвертировать глоссарий из формата ChatGPT (массив объектов) 
    в формат системы (простой JSON объект).
    
    Args:
        input_file: Путь к файлу глоссария от ChatGPT
        output_file: Путь для сохранения конвертированного глоссария
    """
    try:
        # Читаем исходный файл
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Убираем возможные BOM и лишние пробелы
            content = content.strip()
            if content.startswith('\ufeff'):
                content = content[1:]
            data = json.loads(content)
        
        # Конвертируем в простой формат
        converted = {}
        
        if isinstance(data, list):
            # Формат ChatGPT: массив объектов
            for item in data:
                if isinstance(item, dict) and 'source' in item and 'target' in item:
                    source = item['source']
                    target = item['target']
                    # Используем поле 'usage' если есть, иначе 'target'
                    if 'usage' in item and item['usage']:
                        target = item['usage']
                    converted[source] = target
        elif isinstance(data, dict):
            # Уже в правильном формате
            converted = data
        
        # Сохраняем конвертированный глоссарий
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Конвертировано {len(converted)} записей")
        print(f"✓ Сохранено в {output_file}")
        
        # Показываем первые несколько записей
        print("\nПервые записи:")
        for i, (source, target) in enumerate(list(converted.items())[:5]):
            print(f"  {source} → {target}")
        if len(converted) > 5:
            print(f"  ... и еще {len(converted) - 5} записей")
        
        return converted
        
    except Exception as e:
        print(f"✗ Ошибка конвертации: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 convert_glossary.py <input_file> [output_file]")
        print("Пример: python3 convert_glossary.py pintek_glossary.json glossary.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "glossary.json"
    
    if not os.path.exists(input_file):
        print(f"✗ Файл не найден: {input_file}")
        sys.exit(1)
    
    convert_chatgpt_glossary(input_file, output_file)

