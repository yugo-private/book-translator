"""
Основной модуль переводчика с двухэтапным процессом:
1. Машинный перевод (MT) с кешированием
2. Пост-редактирование через LLM

Улучшения:
- Entity placeholders для корректной обработки имён
- RapidFuzz для fuzzy TM matching
- Кеширование MT результатов
- Улучшенные промпты для детской литературы
"""

from typing import List, Optional, Dict
from mt_engines import get_mt_engine, MTEngine
from llm_post_editor import get_llm_editor, LLMPostEditor
from glossary import Glossary
from docx_handler import DocxHandler
from translation_memory import TranslationMemory
from entity_placeholder import EntityPlaceholder
from mt_cache import get_mt_cache, MTCache
import os
import json


class Translator:
    """Класс для перевода документов с использованием MT + LLM пост-редактирования."""
    
    def __init__(self, mt_engine: str = None, llm_editor: str = None, 
                 use_tm: bool = False, use_cache: bool = True,
                 use_placeholders: bool = True,
                 glossary_file: str = "pintek_glossary.json"):
        """
        Инициализировать переводчик.
        
        Args:
            mt_engine: Название MT движка (deepl, google, yandex)
            llm_editor: Название LLM редактора (gpt4, claude, deepseek, crok)
            use_tm: Использовать ли Translation Memory
            use_cache: Использовать ли кеширование MT
            use_placeholders: Использовать ли placeholders для имён
            glossary_file: Путь к файлу глоссария
        """
        self.mt_engine: MTEngine = get_mt_engine(mt_engine)
        self.llm_editor: LLMPostEditor = get_llm_editor(llm_editor)
        self.glossary = Glossary()
        self.docx_handler = DocxHandler()
        self.tm = TranslationMemory() if use_tm else None
        self.use_tm = use_tm
        
        # Новые компоненты
        self.cache = get_mt_cache() if use_cache else None
        self.use_cache = use_cache
        self.entity_placeholder = EntityPlaceholder(glossary_file) if use_placeholders else None
        self.use_placeholders = use_placeholders
        
        # Загружаем расширенный глоссарий из JSON файла
        self._load_extended_glossary(glossary_file)
        
        print(f"✓ Translator инициализирован:")
        print(f"  - MT Engine: {type(self.mt_engine).__name__}")
        print(f"  - LLM Editor: {type(self.llm_editor).__name__}")
        print(f"  - Translation Memory: {'Да' if use_tm else 'Нет'}")
        print(f"  - MT Cache: {'Да' if use_cache else 'Нет'}")
        print(f"  - Entity Placeholders: {'Да' if use_placeholders else 'Нет'}")
    
    def _load_extended_glossary(self, glossary_file: str):
        """Загрузить расширенный глоссарий из JSON файла."""
        if os.path.exists(glossary_file):
            try:
                with open(glossary_file, 'r', encoding='utf-8') as f:
                    glossary_data = json.load(f)
                
                for entry in glossary_data:
                    source = entry.get('source', '')
                    target = entry.get('target', '')
                    if source and target:
                        self.glossary.add(source, target)
                
                print(f"✓ Загружен глоссарий: {len(glossary_data)} терминов")
            except Exception as e:
                print(f"⚠️ Ошибка загрузки глоссария: {e}")
    
    def translate_text(self, text: str, use_glossary: bool = True) -> str:
        """
        Перевести текст с использованием MT + LLM пост-редактирования.
        
        Args:
            text: Исходный текст на русском
            use_glossary: Использовать ли глоссарий
            
        Returns:
            Переведенный текст
        """
        # Шаг 0: Проверяем Translation Memory
        if self.tm:
            tm_result = self.tm.find_in_tm(text)
            translation, similarity, match_type = tm_result
            
            if match_type in ['exact', 'fuzzy']:
                print(f"✓ Найдено в TM ({match_type}, схожесть: {similarity:.1%})")
                return translation
            elif match_type == 'suggest':
                print(f"ℹ TM предложение (схожесть: {similarity:.1%}) - используем для контекста")
        
        # Шаг 1: Entity Placeholders (до MT)
        entity_mapping = {}
        text_for_mt = text
        
        if self.use_placeholders and self.entity_placeholder:
            text_for_mt, entity_mapping = self.entity_placeholder.mark_entities(text)
            if entity_mapping:
                print(f"  → Заменено {len(entity_mapping)} сущностей на placeholders")
        
        # Шаг 2: Машинный перевод (с кешированием)
        mt_translation = None
        engine_name = type(self.mt_engine).__name__
        
        if self.use_cache and self.cache:
            mt_translation = self.cache.get(text_for_mt, "ru", "en-US", engine_name)
            if mt_translation:
                print(f"✓ MT из кеша")
        
        if mt_translation is None:
            print("→ Выполняется машинный перевод...")
            mt_translation = self.mt_engine.translate(text_for_mt, source_lang="ru", target_lang="en-US")
            
            # Сохраняем в кеш
            if self.use_cache and self.cache:
                self.cache.set(text_for_mt, mt_translation, "ru", "en-US", engine_name)
        
        # Шаг 3: Восстановление сущностей после MT
        if entity_mapping and self.entity_placeholder:
            mt_translation = self.entity_placeholder.restore_entities(mt_translation, entity_mapping)
            print(f"  → Восстановлено {len(entity_mapping)} сущностей")
        
        # Шаг 4: Применяем глоссарий к MT переводу (для проверки)
        if use_glossary:
            mt_translation = self.glossary.apply(mt_translation)
        
        # Шаг 5: LLM пост-редактирование
        print("→ Выполняется пост-редактирование через LLM...")
        glossary_dict = self.glossary.get_all() if use_glossary else None
        
        final_translation = self.llm_editor.post_edit(
            original_text=text,
            translated_text=mt_translation,
            glossary=glossary_dict
        )
        
        # Шаг 6: Финальная проверка глоссария
        if use_glossary:
            final_translation = self.glossary.apply(final_translation)
        
        # Шаг 7: Сохраняем в Translation Memory
        if self.tm:
            self.tm.add(text, final_translation)
        
        return final_translation
    
    def translate_docx(self, input_path: str, output_path: str, 
                      batch_size: int = 3, use_glossary: bool = True):
        """
        Перевести .docx файл.
        
        Args:
            input_path: Путь к исходному .docx файлу
            output_path: Путь для сохранения переведенного файла
            batch_size: Количество параграфов для обработки за раз
            use_glossary: Использовать ли глоссарий
        """
        print(f"\n{'='*60}")
        print(f"ПЕРЕВОД ДОКУМЕНТА")
        print(f"{'='*60}")
        print(f"Входной файл: {input_path}")
        print(f"Выходной файл: {output_path}")
        print(f"{'='*60}\n")
        
        paragraphs = self.docx_handler.read_docx(input_path)
        print(f"✓ Найдено параграфов: {len(paragraphs)}")
        
        # Фильтруем пустые параграфы
        paragraphs = [p for p in paragraphs if p.strip()]
        print(f"✓ Непустых параграфов: {len(paragraphs)}")
        
        translated_paragraphs = []
        total_batches = (len(paragraphs) + batch_size - 1) // batch_size
        
        for batch_num, i in enumerate(range(0, len(paragraphs), batch_size), 1):
            batch = paragraphs[i:i + batch_size]
            batch_text = '\n\n'.join(batch)
            
            print(f"\n--- Батч {batch_num}/{total_batches} ---")
            print(f"Параграфы {i+1}-{min(i+batch_size, len(paragraphs))}")
            
            try:
                translated_batch = self.translate_text(batch_text, use_glossary=use_glossary)
                
                # Разделяем обратно на параграфы
                translated_batch_paragraphs = translated_batch.split('\n\n')
                
                # Если количество совпадает, используем по отдельности
                if len(translated_batch_paragraphs) == len(batch):
                    translated_paragraphs.extend(translated_batch_paragraphs)
                else:
                    # Иначе добавляем весь текст
                    translated_paragraphs.append(translated_batch)
                
                print(f"✓ Батч {batch_num} переведён успешно")
                
            except Exception as e:
                print(f"✗ Ошибка при переводе батча {batch_num}: {e}")
                error_marker = f"[ERROR: Translation failed for batch {batch_num}]"
                translated_paragraphs.append(error_marker)
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"Сохранение: {output_path}")
        self.docx_handler.write_docx(output_path, translated_paragraphs, source_docx=input_path)
        
        # Выводим статистику
        if self.cache:
            stats = self.cache.get_stats()
            print(f"\nСтатистика MT кеша:")
            print(f"  - Попадания: {stats['hits']}")
            print(f"  - Промахи: {stats['misses']}")
            print(f"  - Hit rate: {stats['hit_rate']}")
        
        print(f"\n✓ ПЕРЕВОД ЗАВЕРШЁН!")
        print(f"{'='*60}\n")
    
    def add_to_glossary(self, source: str, target: str):
        """Добавить запись в глоссарий."""
        self.glossary.add(source, target)
    
    def get_glossary(self) -> Dict[str, str]:
        """Получить весь глоссарий."""
        return self.glossary.get_all()
    
    def get_cache_stats(self) -> Dict:
        """Получить статистику кеша."""
        if self.cache:
            return self.cache.get_stats()
        return {}
