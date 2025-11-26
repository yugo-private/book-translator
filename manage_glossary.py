"""
Утилита для управления глоссарием переводов.
"""

import argparse
import json
from glossary import Glossary


def main():
    parser = argparse.ArgumentParser(description="Управление глоссарием переводов")
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Добавить запись
    add_parser = subparsers.add_parser('add', help='Добавить запись в глоссарий')
    add_parser.add_argument('source', help='Исходный текст (русский)')
    add_parser.add_argument('target', help='Перевод (английский)')
    
    # Показать все записи
    list_parser = subparsers.add_parser('list', help='Показать все записи глоссария')
    
    # Удалить запись
    remove_parser = subparsers.add_parser('remove', help='Удалить запись из глоссария')
    remove_parser.add_argument('source', help='Исходный текст для удаления')
    
    # Импорт из JSON
    import_parser = subparsers.add_parser('import', help='Импортировать глоссарий из JSON файла')
    import_parser.add_argument('file', help='Путь к JSON файлу')
    
    # Импорт из CSV
    import_csv_parser = subparsers.add_parser('import-csv', help='Импортировать глоссарий из CSV файла')
    import_csv_parser.add_argument('file', help='Путь к CSV файлу')
    
    # Экспорт в JSON
    export_parser = subparsers.add_parser('export', help='Экспортировать глоссарий в JSON файл')
    export_parser.add_argument('file', help='Путь для сохранения JSON файла')
    
    args = parser.parse_args()
    
    glossary = Glossary()
    
    if args.command == 'add':
        glossary.add(args.source, args.target)
        print(f"✓ Добавлено: '{args.source}' → '{args.target}'")
    
    elif args.command == 'list':
        items = glossary.get_all()
        if items:
            print("\nГлоссарий:")
            print("-" * 50)
            for source, target in sorted(items.items()):
                print(f"  {source} → {target}")
            print("-" * 50)
            print(f"Всего записей: {len(items)}")
        else:
            print("Глоссарий пуст.")
    
    elif args.command == 'remove':
        if glossary.get(args.source):
            # Нужно удалить из словаря
            glossary.glossary.pop(args.source.lower(), None)
            glossary.save()
            print(f"✓ Удалено: '{args.source}'")
        else:
            print(f"✗ Запись '{args.source}' не найдена")
    
    elif args.command == 'import':
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            for source, target in imported.items():
                glossary.add(source, target)
            print(f"✓ Импортировано {len(imported)} записей из {args.file}")
        except Exception as e:
            print(f"✗ Ошибка импорта: {e}")
    
    elif args.command == 'export':
        try:
            items = glossary.get_all()
            with open(args.file, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            print(f"✓ Экспортировано {len(items)} записей в {args.file}")
        except Exception as e:
            print(f"✗ Ошибка экспорта: {e}")
    
    elif args.command == 'import-csv':
        try:
            import csv
            imported_count = 0
            with open(args.file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Пропускаем заголовок, если есть
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        source = row[0].strip()
                        target = row[1].strip()
                        if source and target:
                            glossary.add(source, target)
                            imported_count += 1
            print(f"✓ Импортировано {imported_count} записей из {args.file}")
        except Exception as e:
            print(f"✗ Ошибка импорта CSV: {e}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

