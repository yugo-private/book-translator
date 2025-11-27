"""
Модуль для кеширования результатов машинного перевода.

Преимущества:
- Экономия денег при повторных запусках
- Ускорение тестирования
- Консистентность результатов
"""

import json
import os
import hashlib
from typing import Dict, Optional
from datetime import datetime


class MTCache:
    """
    Кеш для результатов машинного перевода.
    Хранит результаты по хешу исходного текста.
    """
    
    def __init__(self, cache_file: str = "mt_cache.json"):
        """
        Args:
            cache_file: Путь к файлу кеша
        """
        self.cache_file = cache_file
        self.cache: Dict[str, Dict] = {}
        self.hits = 0  # Счётчик попаданий в кеш
        self.misses = 0  # Счётчик промахов
        self.load()
    
    def load(self):
        """Загрузить кеш из файла."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    print(f"✓ MT кеш загружен: {len(self.cache)} записей")
            except Exception as e:
                print(f"Ошибка загрузки MT кеша: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def save(self):
        """Сохранить кеш в файл."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'cache': self.cache,
                    'metadata': {
                        'last_updated': datetime.now().isoformat(),
                        'total_entries': len(self.cache)
                    }
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения MT кеша: {e}")
    
    def _make_key(self, text: str, source_lang: str, target_lang: str, engine: str) -> str:
        """
        Создать ключ кеша на основе хеша текста и параметров.
        
        Args:
            text: Исходный текст
            source_lang: Исходный язык
            target_lang: Целевой язык
            engine: Название MT движка
            
        Returns:
            SHA256 хеш
        """
        # Создаём строку для хеширования
        cache_string = f"{engine}:{source_lang}:{target_lang}:{text}"
        return hashlib.sha256(cache_string.encode('utf-8')).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str, engine: str) -> Optional[str]:
        """
        Получить перевод из кеша.
        
        Args:
            text: Исходный текст
            source_lang: Исходный язык
            target_lang: Целевой язык
            engine: Название MT движка
            
        Returns:
            Переведённый текст или None
        """
        key = self._make_key(text, source_lang, target_lang, engine)
        
        if key in self.cache:
            self.hits += 1
            entry = self.cache[key]
            return entry.get('translation')
        
        self.misses += 1
        return None
    
    def set(self, text: str, translation: str, source_lang: str, target_lang: str, engine: str):
        """
        Сохранить перевод в кеш.
        
        Args:
            text: Исходный текст
            translation: Переведённый текст
            source_lang: Исходный язык
            target_lang: Целевой язык
            engine: Название MT движка
        """
        key = self._make_key(text, source_lang, target_lang, engine)
        
        self.cache[key] = {
            'source_text': text[:200] + '...' if len(text) > 200 else text,  # Сокращаем для читаемости
            'translation': translation,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'engine': engine,
            'timestamp': datetime.now().isoformat()
        }
        
        self.save()
    
    def has(self, text: str, source_lang: str, target_lang: str, engine: str) -> bool:
        """Проверить, есть ли перевод в кеше."""
        key = self._make_key(text, source_lang, target_lang, engine)
        return key in self.cache
    
    def clear(self):
        """Очистить весь кеш."""
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.save()
        print("✓ MT кеш очищен")
    
    def get_stats(self) -> Dict:
        """Получить статистику использования кеша."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            'total_entries': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }
    
    def estimate_savings(self, cost_per_char: float = 0.00002) -> Dict:
        """
        Оценить экономию от использования кеша.
        
        Args:
            cost_per_char: Стоимость за символ (примерно для DeepL)
            
        Returns:
            Словарь с информацией об экономии
        """
        total_cached_chars = sum(
            len(entry.get('source_text', '')) 
            for entry in self.cache.values()
        )
        
        estimated_savings = total_cached_chars * cost_per_char * self.hits
        
        return {
            'cached_characters': total_cached_chars,
            'cache_hits': self.hits,
            'estimated_savings_usd': f"${estimated_savings:.4f}"
        }


# Глобальный экземпляр кеша
_mt_cache: Optional[MTCache] = None


def get_mt_cache() -> MTCache:
    """Получить глобальный экземпляр MT кеша."""
    global _mt_cache
    if _mt_cache is None:
        _mt_cache = MTCache()
    return _mt_cache


# Тестирование модуля
if __name__ == "__main__":
    cache = MTCache("test_mt_cache.json")
    
    # Тест сохранения
    cache.set(
        text="Привет, мир!",
        translation="Hello, world!",
        source_lang="ru",
        target_lang="en",
        engine="deepl"
    )
    
    # Тест получения
    result = cache.get("Привет, мир!", "ru", "en", "deepl")
    print(f"Результат из кеша: {result}")
    
    # Тест статистики
    print(f"Статистика: {cache.get_stats()}")
    
    # Очистка тестового файла
    os.remove("test_mt_cache.json")

