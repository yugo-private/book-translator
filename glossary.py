"""
Модуль для управления глоссарием переводов.
Глоссарий обеспечивает консистентность перевода имен, терминов и фраз.
"""

import json
import os
from typing import Dict, Optional


class Glossary:
    """Класс для управления глоссарием переводов."""
    
    def __init__(self, glossary_file: str = "glossary.json"):
        self.glossary_file = glossary_file
        self.glossary: Dict[str, str] = {}
        self.load()
    
    def load(self):
        """Загрузить глоссарий из файла."""
        if os.path.exists(self.glossary_file):
            try:
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    self.glossary = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки глоссария: {e}")
                self.glossary = {}
        else:
            self.glossary = {}
            self.save()
    
    def save(self):
        """Сохранить глоссарий в файл."""
        try:
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(self.glossary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения глоссария: {e}")
    
    def add(self, source: str, target: str):
        """Добавить или обновить запись в глоссарии."""
        self.glossary[source.lower()] = target
        self.save()
    
    def get(self, source: str) -> Optional[str]:
        """Получить перевод из глоссария."""
        return self.glossary.get(source.lower())
    
    def apply(self, text: str) -> str:
        """Применить глоссарий к тексту (заменить термины)."""
        result = text
        # Сортируем по длине (от длинных к коротким), чтобы избежать частичных замен
        sorted_items = sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True)
        
        for source, target in sorted_items:
            # Заменяем с учетом регистра
            import re
            pattern = re.compile(re.escape(source), re.IGNORECASE)
            result = pattern.sub(target, result)
        
        return result
    
    def get_all(self) -> Dict[str, str]:
        """Получить весь глоссарий."""
        return self.glossary.copy()

