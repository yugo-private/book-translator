"""
Модуль Translation Memory (TM) для сохранения и повторного использования переводов.
Полезно для обеспечения консистентности в художественных текстах.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


class TranslationMemory:
    """
    Translation Memory для хранения и поиска ранее переведенных сегментов.
    """
    
    def __init__(self, tm_file: str = "translation_memory.json"):
        self.tm_file = tm_file
        self.memory: List[Dict[str, str]] = []
        self.load()
    
    def load(self):
        """Загрузить TM из файла."""
        if os.path.exists(self.tm_file):
            try:
                with open(self.tm_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory = data.get('segments', [])
            except Exception as e:
                print(f"Ошибка загрузки TM: {e}")
                self.memory = []
        else:
            self.memory = []
            self.save()
    
    def save(self):
        """Сохранить TM в файл."""
        try:
            with open(self.tm_file, 'w', encoding='utf-8') as f:
                json.dump({'segments': self.memory}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения TM: {e}")
    
    def add(self, source: str, target: str, metadata: Dict = None):
        """
        Добавить перевод в TM.
        
        Args:
            source: Исходный текст
            target: Переведенный текст
            metadata: Дополнительная информация (например, глава, дата)
        """
        entry = {
            'source': source.strip(),
            'target': target.strip(),
            'metadata': metadata or {}
        }
        # Проверяем на дубликаты
        if not any(e['source'] == entry['source'] for e in self.memory):
            self.memory.append(entry)
            self.save()
    
    def search(self, source: str, similarity_threshold: float = 0.95) -> Optional[Tuple[str, float]]:
        """
        Найти похожий перевод в TM.
        
        Args:
            source: Исходный текст для поиска
            similarity_threshold: Минимальный порог схожести (0-1)
            
        Returns:
            Кортеж (перевод, коэффициент схожести) или None
        """
        source_clean = source.strip().lower()
        best_match = None
        best_similarity = 0.0
        
        for entry in self.memory:
            entry_source = entry['source'].strip().lower()
            similarity = SequenceMatcher(None, source_clean, entry_source).ratio()
            
            if similarity >= similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = entry['target']
        
        if best_match:
            return (best_match, best_similarity)
        return None
    
    def fuzzy_search(self, source: str, min_similarity: float = 0.85) -> List[Tuple[str, str, float]]:
        """
        Найти несколько похожих переводов (fuzzy match).
        
        Args:
            source: Исходный текст
            min_similarity: Минимальный порог схожести
            
        Returns:
            Список кортежей (исходный, перевод, схожесть)
        """
        source_clean = source.strip().lower()
        matches = []
        
        for entry in self.memory:
            entry_source = entry['source'].strip().lower()
            similarity = SequenceMatcher(None, source_clean, entry_source).ratio()
            
            if similarity >= min_similarity:
                matches.append((entry['source'], entry['target'], similarity))
        
        # Сортируем по схожести (от большей к меньшей)
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches
    
    def get_all(self) -> List[Dict[str, str]]:
        """Получить все записи TM."""
        return self.memory.copy()
    
    def clear(self):
        """Очистить TM."""
        self.memory = []
        self.save()
    
    def export_tmx(self, output_file: str):
        """
        Экспортировать TM в формат TMX (Translation Memory eXchange).
        
        Args:
            output_file: Путь к выходному файлу
        """
        tmx_content = '''<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
    <header creationtool="Translation Memory" creationtoolversion="1.0"
            datatype="plaintext" segtype="sentence" adminlang="en"
            srclang="ru" o-tmf="unknown">
    </header>
    <body>
'''
        
        for entry in self.memory:
            source = entry['source'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            target = entry['target'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            tmx_content += f'''        <tu>
            <tuv xml:lang="ru">
                <seg>{source}</seg>
            </tuv>
            <tuv xml:lang="en">
                <seg>{target}</seg>
            </tuv>
        </tu>
'''
        
        tmx_content += '''    </body>
</tmx>'''
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tmx_content)


class TMEnhancedTranslator:
    """
    Расширенный переводчик с поддержкой Translation Memory.
    """
    
    def __init__(self, translator, use_tm: bool = True):
        """
        Args:
            translator: Экземпляр Translator
            use_tm: Использовать ли Translation Memory
        """
        self.translator = translator
        self.tm = TranslationMemory() if use_tm else None
        self.use_tm = use_tm
    
    def translate_with_tm(self, text: str, use_glossary: bool = True) -> str:
        """
        Перевести текст с использованием TM.
        
        Args:
            text: Исходный текст
            use_glossary: Использовать ли глоссарий
            
        Returns:
            Переведенный текст
        """
        if self.tm:
            # Проверяем TM на точное совпадение
            tm_match = self.tm.search(text, similarity_threshold=0.98)
            if tm_match:
                translation, similarity = tm_match
                print(f"✓ Найдено в TM (схожесть: {similarity:.2%})")
                return translation
            
            # Проверяем на fuzzy match (может быть полезно для похожих фраз)
            fuzzy_matches = self.tm.fuzzy_search(text, min_similarity=0.90)
            if fuzzy_matches:
                # Используем лучший match как основу, но все равно переводим для контекста
                print(f"ℹ Найдено {len(fuzzy_matches)} похожих переводов в TM")
        
        # Выполняем обычный перевод
        translation = self.translator.translate_text(text, use_glossary=use_glossary)
        
        # Сохраняем в TM
        if self.tm:
            self.tm.add(text, translation)
        
        return translation

