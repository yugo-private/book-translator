"""
Инструмент для сравнения качества перевода разных LLM.
Анализирует переведенные файлы и создает детальный отчет сравнения.
"""

import os
from docx_handler import DocxHandler
from typing import Dict, List
import json


class TranslationQualityComparator:
    """Класс для сравнения качества переводов."""
    
    def __init__(self, glossary_file: str = "glossary.json"):
        self.glossary_file = glossary_file
        self.glossary = self._load_glossary()
        self.docx_handler = DocxHandler()
    
    def _load_glossary(self) -> Dict[str, str]:
        """Загрузить глоссарий."""
        if os.path.exists(self.glossary_file):
            try:
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки глоссария: {e}")
                return {}
        return {}
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        Анализировать качество перевода в файле.
        
        Args:
            file_path: Путь к переведенному файлу
            
        Returns:
            Словарь с метриками качества
        """
        if not os.path.exists(file_path):
            return None
        
        paragraphs = self.docx_handler.read_docx(file_path)
        
        metrics = {
            'file': os.path.basename(file_path),
            'paragraphs_count': len(paragraphs),
            'total_chars': sum(len(p) for p in paragraphs),
            'glossary_compliance': 0,
            'glossary_violations': [],
            'has_russian_text': False,
            'russian_paragraphs': []
        }
        
        # Проверяем использование глоссария
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            
            # Проверка на русский текст (кириллица)
            if any('\u0400' <= char <= '\u04FF' for char in para):
                metrics['has_russian_text'] = True
                metrics['russian_paragraphs'].append(i + 1)
            
            # Проверка соответствия глоссарию
            for source, target in self.glossary.items():
                source_lower = source.lower()
                target_lower = target.lower()
                
                # Если найдено русское слово вместо английского перевода
                if source_lower in para_lower and target_lower not in para_lower:
                    metrics['glossary_violations'].append({
                        'paragraph': i + 1,
                        'source': source,
                        'expected': target,
                        'text_snippet': para[:100] + '...' if len(para) > 100 else para
                    })
                elif target_lower in para_lower:
                    metrics['glossary_compliance'] += 1
        
        return metrics
    
    def compare_files(self, file_paths: List[str], output_file: str = "quality_comparison_report.txt"):
        """
        Сравнить качество переводов в нескольких файлах.
        
        Args:
            file_paths: Список путей к переведенным файлам
            output_file: Путь для сохранения отчета
        """
        print("=" * 70)
        print("СРАВНЕНИЕ КАЧЕСТВА ПЕРЕВОДОВ")
        print("=" * 70)
        
        results = {}
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                print(f"\nАнализ файла: {os.path.basename(file_path)}")
                metrics = self.analyze_file(file_path)
                if metrics:
                    llm_name = self._extract_llm_name(file_path)
                    results[llm_name] = metrics
        
        # Создаем отчет
        self._generate_report(results, output_file)
        
        # Выводим краткую сводку
        self._print_summary(results)
    
    def _extract_llm_name(self, file_path: str) -> str:
        """Извлечь название LLM из имени файла."""
        filename = os.path.basename(file_path)
        # Формат: Pintek_ch1_EN_gpt4.docx
        if '_' in filename:
            parts = filename.replace('.docx', '').split('_')
            if len(parts) >= 4:
                return parts[-1].upper()
        return "UNKNOWN"
    
    def _generate_report(self, results: Dict, output_file: str):
        """Создать детальный отчет."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("ОТЧЕТ СРАВНЕНИЯ КАЧЕСТВА ПЕРЕВОДОВ\n")
            f.write("=" * 70 + "\n\n")
            
            for llm_name, metrics in sorted(results.items()):
                f.write(f"\n{'='*70}\n")
                f.write(f"LLM: {llm_name}\n")
                f.write(f"{'='*70}\n\n")
                
                f.write(f"Файл: {metrics['file']}\n")
                f.write(f"Параграфов: {metrics['paragraphs_count']}\n")
                f.write(f"Всего символов: {metrics['total_chars']:,}\n\n")
                
                # Проверка глоссария
                f.write("СООТВЕТСТВИЕ ГЛОССАРИЮ:\n")
                f.write("-" * 70 + "\n")
                f.write(f"Правильно использовано терминов: {metrics['glossary_compliance']}\n")
                f.write(f"Нарушений глоссария: {len(metrics['glossary_violations'])}\n")
                
                if metrics['glossary_violations']:
                    f.write("\nНайденные нарушения:\n")
                    for violation in metrics['glossary_violations'][:10]:  # Первые 10
                        f.write(f"  Параграф {violation['paragraph']}: '{violation['source']}' "
                               f"должно быть '{violation['expected']}'\n")
                        f.write(f"    Фрагмент: {violation['text_snippet']}\n\n")
                
                # Проверка на русский текст
                f.write("\nПРОВЕРКА НА РУССКИЙ ТЕКСТ:\n")
                f.write("-" * 70 + "\n")
                if metrics['has_russian_text']:
                    f.write(f"⚠ ВНИМАНИЕ: Найден русский текст в параграфах: {metrics['russian_paragraphs']}\n")
                else:
                    f.write("✓ Русский текст не найден\n")
                
                f.write("\n")
            
            # Сравнительная таблица
            f.write("\n" + "=" * 70 + "\n")
            f.write("СРАВНИТЕЛЬНАЯ ТАБЛИЦА\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"{'LLM':<15} {'Параграфов':<12} {'Глоссарий':<15} {'Русский текст':<15}\n")
            f.write("-" * 70 + "\n")
            
            for llm_name, metrics in sorted(results.items()):
                glossary_status = f"{metrics['glossary_compliance']}✓/{len(metrics['glossary_violations'])}✗"
                russian_status = "✗ ЕСТЬ" if metrics['has_russian_text'] else "✓ НЕТ"
                f.write(f"{llm_name:<15} {metrics['paragraphs_count']:<12} {glossary_status:<15} {russian_status:<15}\n")
        
        print(f"\n✓ Детальный отчет сохранен в {output_file}")
    
    def _print_summary(self, results: Dict):
        """Вывести краткую сводку в консоль."""
        print("\n" + "=" * 70)
        print("КРАТКАЯ СВОДКА")
        print("=" * 70)
        
        print(f"\n{'LLM':<15} {'Параграфов':<12} {'Глоссарий':<15} {'Русский текст':<15}")
        print("-" * 70)
        
        for llm_name, metrics in sorted(results.items()):
            glossary_status = f"{metrics['glossary_compliance']}✓/{len(metrics['glossary_violations'])}✗"
            russian_status = "✗ ЕСТЬ" if metrics['has_russian_text'] else "✓ НЕТ"
            print(f"{llm_name:<15} {metrics['paragraphs_count']:<12} {glossary_status:<15} {russian_status:<15}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Сравнение качества переводов разных LLM")
    parser.add_argument('files', nargs='+', help='Пути к переведенным файлам')
    parser.add_argument('-o', '--output', default='quality_comparison_report.txt', help='Файл отчета')
    
    args = parser.parse_args()
    
    comparator = TranslationQualityComparator()
    comparator.compare_files(args.files, args.output)


if __name__ == "__main__":
    # Автоматический поиск файлов для сравнения
    output_dir = "Output"
    if os.path.exists(output_dir):
        files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                if f.startswith("Pintek_ch1_EN_") and f.endswith(".docx")]
        
        if files:
            print(f"Найдено файлов для сравнения: {len(files)}")
            comparator = TranslationQualityComparator()
            comparator.compare_files(files)
        else:
            print("Файлы для сравнения не найдены в папке Output/")
    else:
        print("Папка Output/ не найдена")

