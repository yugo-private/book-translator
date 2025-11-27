#!/usr/bin/env python3
"""
Скрипт для сравнения качества пост-редактирования всех LLM.

Сравниваем: GPT-4o, Claude, DeepSeek, Grok

Алгоритм:
1. Очищаем TM (свежий перевод)
2. Переводим главу 1 с каждым LLM
3. Сохраняем результаты для сравнения
"""

import os
import sys
from datetime import datetime
import json

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import config
from translator import Translator
from translation_memory import TranslationMemory


def check_api_keys():
    """Проверить наличие API ключей."""
    keys = {
        'OpenAI (GPT-4)': bool(config.OPENAI_API_KEY),
        'Anthropic (Claude)': bool(config.ANTHROPIC_API_KEY),
        'DeepSeek': bool(config.DEEPSEEK_API_KEY),
        'Grok (xAI)': bool(config.GROK_API_KEY),
        'DeepL (MT)': bool(config.DEEPL_API_KEY),
    }
    
    print("\n📋 Проверка API ключей:")
    for name, available in keys.items():
        status = "✅" if available else "❌"
        print(f"   {status} {name}")
    
    return keys


def clear_tm():
    """Очистить Translation Memory для свежего перевода."""
    tm = TranslationMemory()
    tm.clear()
    print("✓ Translation Memory очищена")


def clear_mt_cache():
    """Очистить кеш MT для свежего перевода."""
    cache_file = "mt_cache.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("✓ MT кеш очищен")


def translate_with_llm(llm_name: str, input_file: str, output_file: str):
    """
    Перевести файл с указанным LLM.
    
    Args:
        llm_name: Название LLM (gpt4, claude, deepseek, grok)
        input_file: Путь к входному файлу
        output_file: Путь к выходному файлу
    """
    print(f"\n{'='*60}")
    print(f"🔄 Перевод с {llm_name.upper()}")
    print(f"{'='*60}")
    
    try:
        translator = Translator(
            mt_engine="deepl",
            llm_editor=llm_name,
            use_tm=False,          # Не используем TM для честного сравнения
            use_cache=True,        # Используем MT кеш (экономия)
            use_placeholders=True,
            glossary_file="pintek_glossary.json"
        )
        
        translator.translate_docx(
            input_path=input_file,
            output_path=output_file,
            batch_size=3,
            use_glossary=True
        )
        
        print(f"✅ {llm_name.upper()} завершён: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка {llm_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Сравнить все LLM."""
    
    print("="*70)
    print("🔬 СРАВНЕНИЕ КАЧЕСТВА ПОСТ-РЕДАКТИРОВАНИЯ LLM")
    print("="*70)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Проверяем API ключи
    keys = check_api_keys()
    
    # Входной файл
    input_file = "Input/Pintek ch1 RU.docx"
    if not os.path.exists(input_file):
        print(f"❌ Файл не найден: {input_file}")
        return
    
    # Создаём директорию Output
    os.makedirs("Output", exist_ok=True)
    
    # Timestamp для файлов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Определяем LLM для тестирования
    llms_to_test = []
    
    if keys['OpenAI (GPT-4)']:
        llms_to_test.append(('gpt4', f'Output/Pintek_ch1_GPT4_{timestamp}.docx'))
    
    if keys['Anthropic (Claude)']:
        llms_to_test.append(('claude', f'Output/Pintek_ch1_Claude_{timestamp}.docx'))
    
    if keys['DeepSeek']:
        llms_to_test.append(('deepseek', f'Output/Pintek_ch1_DeepSeek_{timestamp}.docx'))
    
    if keys['Grok (xAI)']:
        llms_to_test.append(('grok', f'Output/Pintek_ch1_Grok_{timestamp}.docx'))
    
    if not llms_to_test:
        print("\n❌ Нет доступных LLM API ключей!")
        return
    
    print(f"\n📝 Будут протестированы: {', '.join([l[0].upper() for l in llms_to_test])}")
    
    # Очищаем TM для свежего перевода
    print("\n🧹 Подготовка к сравнению...")
    clear_tm()
    # НЕ очищаем MT кеш - экономим на DeepL
    
    # Результаты
    results = {}
    
    # Переводим с каждым LLM
    for llm_name, output_file in llms_to_test:
        success = translate_with_llm(llm_name, input_file, output_file)
        results[llm_name] = {
            'success': success,
            'output_file': output_file if success else None
        }
    
    # Итоговый отчёт
    print("\n" + "="*70)
    print("📊 ИТОГОВЫЙ ОТЧЁТ")
    print("="*70)
    
    successful = []
    failed = []
    
    for llm_name, result in results.items():
        if result['success']:
            successful.append(llm_name)
            print(f"✅ {llm_name.upper()}: {result['output_file']}")
        else:
            failed.append(llm_name)
            print(f"❌ {llm_name.upper()}: Ошибка")
    
    print(f"\n📈 Успешно: {len(successful)}/{len(results)}")
    
    if successful:
        print("\n📁 Файлы для сравнения:")
        for llm_name in successful:
            print(f"   - {results[llm_name]['output_file']}")
    
    # Сохраняем отчёт
    report = {
        'timestamp': timestamp,
        'input_file': input_file,
        'results': results,
        'successful': successful,
        'failed': failed
    }
    
    report_file = f"Output/comparison_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 Отчёт сохранён: {report_file}")
    print("\n" + "="*70)
    print("✅ СРАВНЕНИЕ ЗАВЕРШЕНО!")
    print("="*70)
    print("\n💡 Откройте файлы в Word и сравните качество перевода.")


if __name__ == "__main__":
    main()

