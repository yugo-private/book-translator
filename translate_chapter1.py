#!/usr/bin/env python3
"""
Скрипт для тестового перевода главы 1 книги "Пинтек" с улучшенным алгоритмом.

Запуск:
    python translate_chapter1.py
"""

import os
import sys
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translator import Translator


def main():
    """Перевести главу 1 книги Пинтек."""
    
    print("="*70)
    print("ТЕСТОВЫЙ ПЕРЕВОД ГЛАВЫ 1 - УЛУЧШЕННЫЙ АЛГОРИТМ")
    print("="*70)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Пути к файлам
    input_file = "Input/Pintek ch1 RU.docx"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Output/Pintek_ch1_EN_{timestamp}.docx"
    
    # Проверяем наличие входного файла
    if not os.path.exists(input_file):
        print(f"❌ Файл не найден: {input_file}")
        return
    
    # Создаём директорию Output если нет
    os.makedirs("Output", exist_ok=True)
    
    # Инициализируем переводчик с улучшениями
    print("\nИнициализация переводчика...")
    try:
        translator = Translator(
            mt_engine="deepl",       # DeepL для MT
            llm_editor="gpt4",       # GPT-4o для пост-редактирования
            use_tm=True,             # Включаем Translation Memory
            use_cache=True,          # Включаем кеширование MT
            use_placeholders=True,   # Включаем placeholders для имён
            glossary_file="pintek_glossary.json"
        )
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Запускаем перевод
    print(f"\nВходной файл: {input_file}")
    print(f"Выходной файл: {output_file}")
    print("\nНачинаем перевод...\n")
    
    try:
        translator.translate_docx(
            input_path=input_file,
            output_path=output_file,
            batch_size=3,            # 3 параграфа за раз
            use_glossary=True
        )
        
        print(f"\n✅ ПЕРЕВОД УСПЕШНО ЗАВЕРШЁН!")
        print(f"Результат сохранён: {output_file}")
        
        # Выводим итоговую статистику
        cache_stats = translator.get_cache_stats()
        if cache_stats:
            print(f"\n📊 Статистика кеша MT:")
            print(f"   - Всего записей: {cache_stats.get('total_entries', 0)}")
            print(f"   - Попадания: {cache_stats.get('hits', 0)}")
            print(f"   - Промахи: {cache_stats.get('misses', 0)}")
            print(f"   - Hit rate: {cache_stats.get('hit_rate', '0%')}")
        
    except Exception as e:
        print(f"\n❌ Ошибка при переводе: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

