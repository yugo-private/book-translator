"""
Основной модуль переводчика с двухэтапным процессом:
1. Машинный перевод (MT)
2. Пост-редактирование через LLM
"""

from typing import List, Optional, Dict
from mt_engines import get_mt_engine, MTEngine
from llm_post_editor import get_llm_editor, LLMPostEditor
from glossary import Glossary
from docx_handler import DocxHandler
from translation_memory import TranslationMemory
import os


class Translator:
    """Класс для перевода документов с использованием MT + LLM пост-редактирования."""
    
    def __init__(self, mt_engine: str = None, llm_editor: str = None, use_tm: bool = False):
        """
        Инициализировать переводчик.
        
        Args:
            mt_engine: Название MT движка (deepl, google, yandex)
            llm_editor: Название LLM редактора (gpt4, claude, deepseek, crok)
            use_tm: Использовать ли Translation Memory
        """
        self.mt_engine: MTEngine = get_mt_engine(mt_engine)
        self.llm_editor: LLMPostEditor = get_llm_editor(llm_editor)
        self.glossary = Glossary()
        self.docx_handler = DocxHandler()
        self.tm = TranslationMemory() if use_tm else None
        self.use_tm = use_tm
    
    def translate_text(self, text: str, use_glossary: bool = True) -> str:
        """
        Перевести текст с использованием MT + LLM пост-редактирования.
        
        Args:
            text: Исходный текст на русском
            use_glossary: Использовать ли глоссарий
            
        Returns:
            Переведенный текст
        """
        # Проверяем Translation Memory
        if self.tm:
            tm_match = self.tm.search(text, similarity_threshold=0.98)
            if tm_match:
                translation, similarity = tm_match
                print(f"✓ Найдено в Translation Memory (схожесть: {similarity:.2%})")
                return translation
        
        # Этап 1: Машинный перевод
        print("Выполняется машинный перевод...")
        mt_translation = self.mt_engine.translate(text, source_lang="ru", target_lang="en-US")
        
        # Применяем глоссарий к MT переводу
        if use_glossary:
            mt_translation = self.glossary.apply(mt_translation)
        
        # Этап 2: LLM пост-редактирование
        print("Выполняется пост-редактирование через LLM...")
        glossary_dict = self.glossary.get_all() if use_glossary else None
        final_translation = self.llm_editor.post_edit(
            original_text=text,
            translated_text=mt_translation,
            glossary=glossary_dict
        )
        
        # Сохраняем в Translation Memory
        if self.tm:
            self.tm.add(text, final_translation)
        
        return final_translation
    
    def translate_docx(self, input_path: str, output_path: str, 
                      batch_size: int = 5, use_glossary: bool = True):
        """
        Перевести .docx файл.
        
        Args:
            input_path: Путь к исходному .docx файлу
            output_path: Путь для сохранения переведенного файла
            batch_size: Количество параграфов для обработки за раз (для оптимизации)
            use_glossary: Использовать ли глоссарий
        """
        print(f"Чтение файла: {input_path}")
        paragraphs = self.docx_handler.read_docx(input_path)
        print(f"Найдено параграфов: {len(paragraphs)}")
        
        translated_paragraphs = []
        
        # Обрабатываем параграфы батчами для оптимизации
        for i in range(0, len(paragraphs), batch_size):
            batch = paragraphs[i:i + batch_size]
            batch_text = '\n\n'.join(batch)
            
            print(f"Обработка параграфов {i+1}-{min(i+batch_size, len(paragraphs))} из {len(paragraphs)}...")
            
            try:
                translated_batch = self.translate_text(batch_text, use_glossary=use_glossary)
                # Разделяем обратно на параграфы (простое разделение по двойным переносам)
                translated_batch_paragraphs = translated_batch.split('\n\n')
                
                # Если количество не совпадает, используем весь текст как один параграф
                if len(translated_batch_paragraphs) == len(batch):
                    translated_paragraphs.extend(translated_batch_paragraphs)
                else:
                    translated_paragraphs.append(translated_batch)
                
            except Exception as e:
                print(f"Ошибка при переводе батча {i+1}: {e}")
                # В случае ошибки добавляем маркер ошибки вместо оригинала
                error_marker = f"[ERROR: Translation failed for batch {i+1}]"
                translated_paragraphs.append(error_marker)
                import traceback
                traceback.print_exc()
        
        print(f"Сохранение переведенного файла: {output_path}")
        self.docx_handler.write_docx(output_path, translated_paragraphs, source_docx=input_path)
        print("Перевод завершен!")
    
    def add_to_glossary(self, source: str, target: str):
        """Добавить запись в глоссарий."""
        self.glossary.add(source, target)
    
    def get_glossary(self) -> Dict[str, str]:
        """Получить весь глоссарий."""
        return self.glossary.get_all()

