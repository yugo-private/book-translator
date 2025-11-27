"""
Модуль для обработки имён и сущностей с помощью placeholders.

Проблема: Русские имена склоняются (Артём → Артёма → Артёму), 
что может привести к некорректному переводу.

Решение: 
1. До MT заменяем исходные сущности плейсхолдерами (__ENT_1__, __ENT_2__)
2. После MT и LLM подставляем целевые формы из глоссария
"""

import re
import json
from typing import Dict, List, Tuple, Optional


class EntityPlaceholder:
    """
    Класс для замены сущностей (имён, мест, артефактов) на плейсхолдеры.
    Это помогает избежать проблем со склонениями русских имён при переводе.
    """
    
    def __init__(self, glossary_file: str = "pintek_glossary.json"):
        """
        Args:
            glossary_file: Путь к файлу глоссария в формате JSON
        """
        self.glossary_file = glossary_file
        self.entities: Dict[str, Dict] = {}  # source -> {target, type, ...}
        self.source_forms: Dict[str, str] = {}  # форма -> базовая форма
        self.load_glossary()
    
    def load_glossary(self):
        """Загрузить глоссарий и извлечь сущности."""
        try:
            with open(self.glossary_file, 'r', encoding='utf-8') as f:
                glossary_data = json.load(f)
            
            for entry in glossary_data:
                source = entry.get('source', '')
                target = entry.get('target', '')
                entity_type = entry.get('type', 'unknown')
                
                if source and target:
                    self.entities[source] = {
                        'target': target,
                        'type': entity_type,
                        'case_sensitive': entry.get('case_sensitive', True),
                        'note': entry.get('note', '')
                    }
                    
                    # Добавляем возможные формы склонений для русских имён
                    self._add_russian_forms(source, target)
            
            print(f"✓ Загружено {len(self.entities)} сущностей для placeholder")
            
        except FileNotFoundError:
            print(f"⚠️ Файл глоссария не найден: {self.glossary_file}")
        except Exception as e:
            print(f"Ошибка загрузки глоссария: {e}")
    
    def _add_russian_forms(self, source: str, target: str):
        """
        Добавить возможные падежные формы русского слова.
        Упрощённая версия без pymorphy2.
        """
        # Базовая форма
        self.source_forms[source.lower()] = source
        
        # Добавляем простые варианты склонений для имён
        # (это упрощённый подход, более точный требует pymorphy2)
        if source.endswith('ём') or source.endswith('ем'):
            # Артём -> Артёма, Артёму, Артёмом
            base = source[:-2]
            forms = [
                base + 'ёма', base + 'ема',  # родительный
                base + 'ёму', base + 'ему',  # дательный
                base + 'ёмом', base + 'емом',  # творительный
                base + 'ёме', base + 'еме',  # предложный
            ]
            for form in forms:
                self.source_forms[form.lower()] = source
        
        elif source.endswith('а') or source.endswith('я'):
            # Катя -> Кати, Кате, Катей, Катю
            base = source[:-1]
            suffix = source[-1]
            if suffix == 'я':
                forms = [base + 'и', base + 'е', base + 'ей', base + 'ю']
            else:
                forms = [base + 'ы', base + 'е', base + 'ой', base + 'у']
            for form in forms:
                self.source_forms[form.lower()] = source
        
        elif source.endswith('ек') or source.endswith('ик'):
            # Пинтек -> Пинтека, Пинтеку
            forms = [source + 'а', source + 'у', source + 'ом', source + 'е']
            for form in forms:
                self.source_forms[form.lower()] = source
    
    def mark_entities(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Заменить сущности в тексте на плейсхолдеры.
        
        Args:
            text: Исходный текст на русском
            
        Returns:
            (текст с плейсхолдерами, словарь placeholder -> (source, target))
        """
        mapping = {}
        result = text
        idx = 0
        
        # Сортируем по длине (от длинных к коротким) для корректной замены
        sorted_entities = sorted(self.entities.keys(), key=len, reverse=True)
        
        for source in sorted_entities:
            entity_info = self.entities[source]
            target = entity_info['target']
            case_sensitive = entity_info.get('case_sensitive', True)
            
            # Создаём паттерн для поиска всех форм
            forms_to_find = [source]
            for form, base in self.source_forms.items():
                if base == source:
                    forms_to_find.append(form)
            
            # Удаляем дубликаты и сортируем по длине
            forms_to_find = sorted(set(forms_to_find), key=len, reverse=True)
            
            for form in forms_to_find:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(r'\b' + re.escape(form) + r'\b', flags)
                
                def replace_func(match):
                    nonlocal idx
                    original = match.group(0)
                    placeholder = f"__ENT_{idx}__"
                    mapping[placeholder] = {
                        'original': original,
                        'source': source,
                        'target': target
                    }
                    idx += 1
                    return placeholder
                
                result = pattern.sub(replace_func, result)
        
        return result, mapping
    
    def restore_entities(self, text: str, mapping: Dict[str, Dict]) -> str:
        """
        Восстановить сущности в переведённом тексте.
        
        Args:
            text: Текст с плейсхолдерами (после MT/LLM)
            mapping: Словарь placeholder -> {original, source, target}
            
        Returns:
            Текст с восстановленными сущностями
        """
        result = text
        
        for placeholder, info in mapping.items():
            target = info['target']
            original = info['original']
            
            # Проверяем регистр оригинала для сохранения капитализации
            if original[0].isupper():
                target = target[0].upper() + target[1:] if len(target) > 1 else target.upper()
            
            result = result.replace(placeholder, target)
        
        return result
    
    def process_text(self, text: str) -> Tuple[str, Dict]:
        """
        Подготовить текст для перевода (заменить сущности).
        
        Returns:
            (текст_с_плейсхолдерами, mapping)
        """
        return self.mark_entities(text)
    
    def finalize_text(self, text: str, mapping: Dict) -> str:
        """
        Финализировать текст после перевода (восстановить сущности).
        """
        return self.restore_entities(text, mapping)
    
    def get_entity_list(self) -> List[str]:
        """Получить список всех сущностей."""
        return list(self.entities.keys())
    
    def get_target_for_source(self, source: str) -> Optional[str]:
        """Получить целевой перевод для исходной формы."""
        # Проверяем точное совпадение
        if source in self.entities:
            return self.entities[source]['target']
        
        # Проверяем формы склонений
        base = self.source_forms.get(source.lower())
        if base and base in self.entities:
            return self.entities[base]['target']
        
        return None


def create_entity_placeholder(glossary_file: str = "pintek_glossary.json") -> EntityPlaceholder:
    """Создать экземпляр EntityPlaceholder."""
    return EntityPlaceholder(glossary_file)


# Тестирование модуля
if __name__ == "__main__":
    ep = EntityPlaceholder()
    
    test_text = """
    Артём посмотрел на Катю. Они вместе пошли к Пинтеку.
    — Пинтек, помоги нам! — попросил Артём.
    Катя взяла синюю тетрадь и открыла её.
    """
    
    print("Исходный текст:")
    print(test_text)
    
    marked_text, mapping = ep.mark_entities(test_text)
    print("\nТекст с плейсхолдерами:")
    print(marked_text)
    print("\nMapping:")
    for k, v in mapping.items():
        print(f"  {k}: {v}")
    
    # Симуляция перевода (просто оставляем плейсхолдеры)
    translated = marked_text.replace("посмотрел на", "looked at")
    
    restored = ep.restore_entities(translated, mapping)
    print("\nВосстановленный текст:")
    print(restored)

