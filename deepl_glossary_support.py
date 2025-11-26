"""
Модуль для поддержки глоссариев DeepL API.
DeepL позволяет создавать глоссарии через API и использовать их при переводе.
"""

import deepl
from typing import Dict, Optional


class DeepLGlossaryManager:
    """Менеджер глоссариев DeepL."""
    
    def __init__(self, api_key: str):
        """
        Инициализировать менеджер глоссариев.
        
        Args:
            api_key: DeepL API ключ
        """
        self.translator = deepl.Translator(api_key)
        self.glossary_id: Optional[str] = None
    
    def create_glossary(self, glossary: Dict[str, str], glossary_name: str = "book_glossary") -> str:
        """
        Создать глоссарий в DeepL.
        
        Args:
            glossary: Словарь {русский_термин: английский_перевод}
            glossary_name: Имя глоссария
            
        Returns:
            ID созданного глоссария
        """
        try:
            # Преобразуем словарь в список кортежей (source, target)
            entries = list(glossary.items())
            
            # Создаем глоссарий в DeepL
            # Формат: (source_term, target_term) пары
            result = self.translator.create_glossary(
                name=glossary_name,
                source_lang="RU",
                target_lang="EN-US",
                entries=entries
            )
            
            self.glossary_id = result.glossary_id
            print(f"✓ Глоссарий создан в DeepL: {glossary_name} (ID: {self.glossary_id})")
            return self.glossary_id
            
        except Exception as e:
            print(f"✗ Ошибка создания глоссария в DeepL: {e}")
            # DeepL может не поддерживать глоссарии на бесплатном тарифе
            print("Примечание: Глоссарии DeepL доступны только на платных тарифах")
            return None
    
    def list_glossaries(self):
        """Получить список всех глоссариев."""
        try:
            glossaries = self.translator.list_glossaries()
            return glossaries
        except Exception as e:
            print(f"Ошибка получения списка глоссариев: {e}")
            return []
    
    def delete_glossary(self, glossary_id: str):
        """Удалить глоссарий."""
        try:
            self.translator.delete_glossary(glossary_id)
            print(f"✓ Глоссарий удален: {glossary_id}")
        except Exception as e:
            print(f"✗ Ошибка удаления глоссария: {e}")


def translate_with_deepl_glossary(
    text: str,
    api_key: str,
    glossary_id: Optional[str] = None,
    source_lang: str = "RU",
    target_lang: str = "EN-US"
) -> str:
    """
    Перевести текст через DeepL с использованием глоссария.
    
    Args:
        text: Текст для перевода
        api_key: DeepL API ключ
        glossary_id: ID глоссария в DeepL (если есть)
        source_lang: Исходный язык
        target_lang: Целевой язык
        
    Returns:
        Переведенный текст
    """
    translator = deepl.Translator(api_key)
    
    # Если есть glossary_id, используем его
    if glossary_id:
        result = translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=target_lang,
            glossary=glossary_id  # Передаем ID глоссария
        )
    else:
        result = translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
    
    return result.text

