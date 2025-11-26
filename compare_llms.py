"""
Автоматический скрипт для сравнения качества перевода разных LLM.
Переводит первую главу всеми доступными LLM и создает отчет сравнения.
"""

import os
import sys
from translator import Translator
from config import *
from docx_handler import DocxHandler


def check_available_llms():
    """Проверить, какие LLM доступны."""
    available = []
    
    if OPENAI_API_KEY and len(OPENAI_API_KEY) > 10:
        available.append('gpt4')
    if ANTHROPIC_API_KEY and len(ANTHROPIC_API_KEY) > 10:
        available.append('claude')
    if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10:
        available.append('deepseek')
    if GROK_API_KEY and len(GROK_API_KEY) > 10:
        available.append('grok')
    if CROK_API_KEY and len(CROK_API_KEY) > 10:
        available.append('crok')
    
    return available


def translate_with_llm(input_file: str, output_file: str, llm_name: str):
    """
    Перевести файл с использованием указанного LLM.
    
    Args:
        input_file: Путь к исходному файлу
        output_file: Путь для сохранения перевода
        llm_name: Название LLM (gpt4, claude, deepseek, grok, crok)
    """
    print(f"\n{'='*60}")
    print(f"Перевод с использованием: {llm_name.upper()}")
    print(f"{'='*60}")
    
    try:
        translator = Translator(
            mt_engine="deepl",
            llm_editor=llm_name,
            use_tm=True
        )
        
        translator.translate_docx(
            input_path=input_file,
            output_path=output_file,
            batch_size=3,
            use_glossary=True
        )
        
        print(f"✓ Перевод завершен: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка при переводе с {llm_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_comparison_report(results: dict, output_file: str = "llm_comparison_report.txt"):
    """
    Создать отчет сравнения LLM.
    
    Args:
        results: Словарь с результатами {llm_name: success}
        output_file: Путь для сохранения отчета
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ОТЧЕТ СРАВНЕНИЯ КАЧЕСТВА ПЕРЕВОДА РАЗНЫХ LLM\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("ПЕРЕВЕДЕНО УСПЕШНО:\n")
        f.write("-" * 70 + "\n")
        successful = [llm for llm, success in results.items() if success]
        failed = [llm for llm, success in results.items() if not success]
        
        for i, llm in enumerate(successful, 1):
            f.write(f"{i}. {llm.upper()}\n")
            f.write(f"   Файл: Output/Pintek_ch1_EN_{llm}.docx\n\n")
        
        if failed:
            f.write("\nОШИБКИ ПРИ ПЕРЕВОДЕ:\n")
            f.write("-" * 70 + "\n")
            for llm in failed:
                f.write(f"✗ {llm.upper()}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("ИНСТРУКЦИИ ДЛЯ СРАВНЕНИЯ:\n")
        f.write("=" * 70 + "\n\n")
        f.write("1. Откройте все переведенные файлы в папке Output/\n")
        f.write("2. Сравните качество перевода:\n")
        f.write("   - Естественность языка\n")
        f.write("   - Сохранение стиля оригинала\n")
        f.write("   - Правильность использования глоссария\n")
        f.write("   - Эмоциональная окраска\n")
        f.write("3. Выберите лучший вариант для дальнейшей работы\n\n")
        
        f.write("ФАЙЛЫ ДЛЯ СРАВНЕНИЯ:\n")
        f.write("-" * 70 + "\n")
        for llm in successful:
            f.write(f"- Output/Pintek_ch1_EN_{llm}.docx\n")
    
    print(f"\n✓ Отчет сохранен в {output_file}")


def main():
    input_file = "Input/Pintek ch1 RU.docx"
    
    # Проверяем наличие исходного файла
    if not os.path.exists(input_file):
        print(f"✗ Файл не найден: {input_file}")
        print("Убедитесь, что файл находится в папке Input/")
        return
    
    # Проверяем доступные LLM
    available_llms = check_available_llms()
    
    if not available_llms:
        print("✗ Не найдено доступных LLM!")
        print("Проверьте файл .env и убедитесь, что API ключи добавлены.")
        return
    
    print("=" * 70)
    print("АВТОМАТИЧЕСКОЕ СРАВНЕНИЕ LLM ДЛЯ ПЕРЕВОДА")
    print("=" * 70)
    print(f"\nИсходный файл: {input_file}")
    print(f"\nНайдено доступных LLM: {len(available_llms)}")
    for llm in available_llms:
        print(f"  - {llm.upper()}")
    
    print("\nНачинаю перевод всеми доступными LLM...")
    print("Это может занять некоторое время (примерно 2-5 минут на каждый LLM).\n")
    
    # Создаем папку Output если её нет
    os.makedirs("Output", exist_ok=True)
    
    results = {}
    
    # Переводим каждым доступным LLM
    for llm in available_llms:
        output_file = f"Output/Pintek_ch1_EN_{llm}.docx"
        success = translate_with_llm(input_file, output_file, llm)
        results[llm] = success
    
    # Создаем отчет
    create_comparison_report(results)
    
    # Итоговая сводка
    print("\n" + "=" * 70)
    print("ИТОГОВАЯ СВОДКА")
    print("=" * 70)
    successful_count = sum(1 for success in results.values() if success)
    print(f"\nУспешно переведено: {successful_count} из {len(available_llms)}")
    print(f"\nПереведенные файлы находятся в папке Output/:")
    for llm, success in results.items():
        if success:
            print(f"  ✓ Pintek_ch1_EN_{llm}.docx")
        else:
            print(f"  ✗ {llm.upper()} - ошибка")
    
    print(f"\n✓ Отчет сравнения: llm_comparison_report.txt")
    print("\nТеперь откройте файлы и сравните качество перевода!")


if __name__ == "__main__":
    main()

