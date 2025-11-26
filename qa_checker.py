"""
Модуль для контроля качества (QA) перевода.
"""

import json
import os
from typing import List, Dict, Tuple
from docx_handler import DocxHandler


class QAChecker:
    """Класс для проверки качества перевода."""
    
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
    
    def check_glossary_compliance(self, translated_text: str) -> List[Dict]:
        """
        Проверить соответствие перевода глоссарию.
        
        Args:
            translated_text: Переведенный текст
            
        Returns:
            Список найденных проблем
        """
        issues = []
        translated_lower = translated_text.lower()
        
        for source, target in self.glossary.items():
            source_lower = source.lower()
            target_lower = target.lower()
            
            # Проверяем, используется ли правильный перевод из глоссария
            if source_lower in translated_lower:
                # Если исходное слово найдено в переводе - это проблема
                issues.append({
                    'type': 'glossary_violation',
                    'source': source,
                    'expected': target,
                    'severity': 'high',
                    'message': f"Найдено русское слово '{source}' в переводе. Ожидается '{target}'"
                })
            
            # Проверяем, используется ли правильный перевод
            if target_lower not in translated_lower and source_lower in translated_lower:
                issues.append({
                    'type': 'missing_translation',
                    'source': source,
                    'expected': target,
                    'severity': 'high',
                    'message': f"Слово '{source}' не переведено как '{target}'"
                })
        
        return issues
    
    def check_consistency(self, translated_paragraphs: List[str]) -> List[Dict]:
        """
        Проверить консистентность перевода между параграфами.
        
        Args:
            translated_paragraphs: Список переведенных параграфов
            
        Returns:
            Список найденных проблем
        """
        issues = []
        
        # Проверяем использование терминов из глоссария
        for i, para in enumerate(translated_paragraphs):
            para_issues = self.check_glossary_compliance(para)
            for issue in para_issues:
                issue['paragraph'] = i + 1
                issues.append(issue)
        
        return issues
    
    def check_docx(self, original_file: str, translated_file: str) -> Dict:
        """
        Проверить качество перевода документа.
        
        Args:
            original_file: Путь к оригинальному файлу
            translated_file: Путь к переведенному файлу
            
        Returns:
            Словарь с результатами проверки
        """
        print(f"Проверка качества перевода...")
        print(f"Оригинал: {original_file}")
        print(f"Перевод: {translated_file}")
        
        original_paras = self.docx_handler.read_docx(original_file)
        translated_paras = self.docx_handler.read_docx(translated_file)
        
        results = {
            'original_paragraphs': len(original_paras),
            'translated_paragraphs': len(translated_paras),
            'issues': [],
            'warnings': []
        }
        
        # Проверка количества параграфов
        if len(original_paras) != len(translated_paras):
            results['warnings'].append({
                'type': 'paragraph_count_mismatch',
                'message': f"Количество параграфов не совпадает: оригинал {len(original_paras)}, перевод {len(translated_paras)}"
            })
        
        # Проверка соответствия глоссарию
        glossary_issues = self.check_consistency(translated_paras)
        results['issues'].extend(glossary_issues)
        
        # Статистика
        results['glossary_violations'] = len([i for i in glossary_issues if i['type'] == 'glossary_violation'])
        results['missing_translations'] = len([i for i in glossary_issues if i['type'] == 'missing_translation'])
        
        return results
    
    def generate_report(self, results: Dict, output_file: str = "qa_report.txt"):
        """
        Сгенерировать отчет о проверке качества.
        
        Args:
            results: Результаты проверки
            output_file: Путь для сохранения отчета
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ОТЧЕТ О КОНТРОЛЕ КАЧЕСТВА ПЕРЕВОДА\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Оригинальных параграфов: {results['original_paragraphs']}\n")
            f.write(f"Переведенных параграфов: {results['translated_paragraphs']}\n\n")
            
            if results['warnings']:
                f.write("ПРЕДУПРЕЖДЕНИЯ:\n")
                f.write("-" * 60 + "\n")
                for warning in results['warnings']:
                    f.write(f"⚠ {warning['message']}\n")
                f.write("\n")
            
            if results['issues']:
                f.write(f"НАЙДЕННЫЕ ПРОБЛЕМЫ: {len(results['issues'])}\n")
                f.write("-" * 60 + "\n")
                
                high_severity = [i for i in results['issues'] if i['severity'] == 'high']
                if high_severity:
                    f.write(f"\nКРИТИЧЕСКИЕ ПРОБЛЕМЫ ({len(high_severity)}):\n")
                    for issue in high_severity:
                        para_info = f" (параграф {issue.get('paragraph', '?')})" if 'paragraph' in issue else ""
                        f.write(f"✗ {issue['message']}{para_info}\n")
                
                f.write(f"\nСтатистика:\n")
                f.write(f"  - Нарушения глоссария: {results['glossary_violations']}\n")
                f.write(f"  - Отсутствующие переводы: {results['missing_translations']}\n")
            else:
                f.write("✓ Проблем не найдено!\n")
        
        print(f"\n✓ Отчет сохранен в {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Проверка качества перевода")
    parser.add_argument('original', help='Путь к оригинальному файлу')
    parser.add_argument('translated', help='Путь к переведенному файлу')
    parser.add_argument('-o', '--output', default='qa_report.txt', help='Файл для отчета')
    
    args = parser.parse_args()
    
    checker = QAChecker()
    results = checker.check_docx(args.original, args.translated)
    checker.generate_report(results, args.output)
    
    # Выводим краткую сводку
    print("\n" + "=" * 60)
    print("КРАТКАЯ СВОДКА:")
    print("=" * 60)
    print(f"Параграфов: {results['original_paragraphs']} → {results['translated_paragraphs']}")
    print(f"Проблем найдено: {len(results['issues'])}")
    print(f"Предупреждений: {len(results['warnings'])}")
    if results['issues']:
        print(f"\nКритических проблем: {len([i for i in results['issues'] if i['severity'] == 'high'])}")


if __name__ == "__main__":
    main()

