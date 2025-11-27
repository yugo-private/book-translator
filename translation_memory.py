"""
Модуль Translation Memory (TM) для сохранения и повторного использования переводов.
Полезно для обеспечения консистентности в художественных текстах.

Улучшения:
- RapidFuzz для более точного fuzzy matching
- Нормализация текста перед поиском
- Три уровня совпадений: exact, fuzzy, suggest
"""

import json
import os
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

# Используем RapidFuzz для быстрого и точного fuzzy matching
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    from difflib import SequenceMatcher
    RAPIDFUZZ_AVAILABLE = False
    print("⚠️ RapidFuzz не установлен. Используем стандартный SequenceMatcher (медленнее).")


def normalize_text(text: str) -> str:
    """
    Нормализовать текст для поиска в TM.
    - Приводит к нижнему регистру
    - Удаляет лишние пробелы
    - Нормализует Unicode
    - Удаляет пунктуацию для сравнения
    """
    text = text.strip().lower()
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', ' ', text)  # Нормализуем пробелы
    return text


def normalize_for_comparison(text: str) -> str:
    """
    Более агрессивная нормализация для сравнения.
    Удаляет пунктуацию и лишние символы.
    """
    text = normalize_text(text)
    text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
    return text


class TranslationMemory:
    """
    Translation Memory для хранения и поиска ранее переведенных сегментов.
    Использует RapidFuzz для быстрого и точного fuzzy matching.
    """
    
    # Пороги для разных типов совпадений
    EXACT_THRESHOLD = 0.98      # 98%+ = exact match
    FUZZY_THRESHOLD = 0.95      # 95%+ = fuzzy match (автоматически использовать)
    SUGGEST_THRESHOLD = 0.80    # 80-95% = suggest (для ручной проверки)
    
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
                print(f"✓ TM загружена: {len(self.memory)} сегментов")
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
    
    def search(self, source: str, similarity_threshold: float = None) -> Optional[Tuple[str, float, str]]:
        """
        Найти похожий перевод в TM с использованием RapidFuzz.
        
        Args:
            source: Исходный текст для поиска
            similarity_threshold: Минимальный порог схожести (по умолчанию FUZZY_THRESHOLD)
            
        Returns:
            Кортеж (перевод, коэффициент схожести, тип_совпадения) или None
            тип_совпадения: 'exact', 'fuzzy', 'suggest'
        """
        if similarity_threshold is None:
            similarity_threshold = self.FUZZY_THRESHOLD
            
        if not self.memory:
            return None
            
        source_norm = normalize_text(source)
        source_cmp = normalize_for_comparison(source)
        
        best_match = None
        best_similarity = 0.0
        match_type = 'none'
        
        for entry in self.memory:
            entry_norm = normalize_text(entry['source'])
            entry_cmp = normalize_for_comparison(entry['source'])
            
            # Вычисляем схожесть
            if RAPIDFUZZ_AVAILABLE:
                # RapidFuzz возвращает значение 0-100
                similarity = fuzz.ratio(source_cmp, entry_cmp) / 100.0
            else:
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, source_cmp, entry_cmp).ratio()
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry['target']
                
                # Определяем тип совпадения
                if similarity >= self.EXACT_THRESHOLD:
                    match_type = 'exact'
                elif similarity >= self.FUZZY_THRESHOLD:
                    match_type = 'fuzzy'
                elif similarity >= self.SUGGEST_THRESHOLD:
                    match_type = 'suggest'
                else:
                    match_type = 'none'
        
        if best_match and best_similarity >= self.SUGGEST_THRESHOLD:
            return (best_match, best_similarity, match_type)
        return None
    
    def find_in_tm(self, source: str) -> Tuple[Optional[str], float, str]:
        """
        Найти перевод в TM с возвратом типа совпадения.
        
        Returns:
            (перевод или None, схожесть, тип: 'exact'|'fuzzy'|'suggest'|'none')
        """
        result = self.search(source, similarity_threshold=self.SUGGEST_THRESHOLD)
        if result:
            return result
        return (None, 0.0, 'none')
    
    def fuzzy_search(self, source: str, min_similarity: float = None) -> List[Tuple[str, str, float, str]]:
        """
        Найти несколько похожих переводов (fuzzy match).
        
        Args:
            source: Исходный текст
            min_similarity: Минимальный порог схожести
            
        Returns:
            Список кортежей (исходный, перевод, схожесть, тип)
        """
        if min_similarity is None:
            min_similarity = self.SUGGEST_THRESHOLD
            
        source_cmp = normalize_for_comparison(source)
        matches = []
        
        for entry in self.memory:
            entry_cmp = normalize_for_comparison(entry['source'])
            
            if RAPIDFUZZ_AVAILABLE:
                similarity = fuzz.ratio(source_cmp, entry_cmp) / 100.0
            else:
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, source_cmp, entry_cmp).ratio()
            
            if similarity >= min_similarity:
                if similarity >= self.EXACT_THRESHOLD:
                    match_type = 'exact'
                elif similarity >= self.FUZZY_THRESHOLD:
                    match_type = 'fuzzy'
                else:
                    match_type = 'suggest'
                    
                matches.append((entry['source'], entry['target'], similarity, match_type))
        
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

