"""
Модули для различных систем машинного перевода (MT).
"""

from typing import Optional
import config


class MTEngine:
    """Базовый класс для MT движков."""
    
    def translate(self, text: str, source_lang: str = "ru", target_lang: str = "en") -> str:
        """Перевести текст."""
        raise NotImplementedError


class DeepLEngine(MTEngine):
    """DeepL API для перевода."""
    
    def __init__(self, api_key: str, glossary_id: str = None):
        if not api_key:
            raise ValueError("DeepL API ключ не указан")
        try:
            import deepl
            self.translator = deepl.Translator(api_key)
            self.glossary_id = glossary_id  # ID глоссария в DeepL (если есть)
        except Exception as e:
            raise ValueError(f"Ошибка инициализации DeepL: {e}")
    
    def translate(self, text: str, source_lang: str = "ru", target_lang: str = "en-US") -> str:
        """Перевести текст через DeepL."""
        try:
            # DeepL требует конкретный вариант английского (EN-US или EN-GB)
            if target_lang.upper() == "EN":
                target_lang = "EN-US"
            
            # Если есть glossary_id, используем его
            translate_params = {
                'text': text,
                'source_lang': source_lang.upper(),
                'target_lang': target_lang.upper()
            }
            
            if self.glossary_id:
                translate_params['glossary'] = self.glossary_id
                print(f"  Используется глоссарий DeepL: {self.glossary_id}")
            
            result = self.translator.translate_text(**translate_params)
            return result.text
        except Exception as e:
            raise Exception(f"Ошибка перевода DeepL: {e}")


class GoogleTranslateEngine(MTEngine):
    """Google Cloud Translation API."""
    
    def __init__(self, api_key: str, project_id: str):
        if not api_key:
            raise ValueError("Google API ключ не указан")
        self.api_key = api_key
        self.project_id = project_id
    
    def translate(self, text: str, source_lang: str = "ru", target_lang: str = "en") -> str:
        """Перевести текст через Google Translate API."""
        try:
            import requests
            
            # Используем REST API Google Translate
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                'key': self.api_key,
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            if 'data' in result and 'translations' in result['data']:
                translations = result['data']['translations']
                return ' '.join([t['translatedText'] for t in translations])
            else:
                raise Exception("Неожиданный формат ответа от Google API")
        except Exception as e:
            raise Exception(f"Ошибка перевода Google: {e}")


class YandexTranslateEngine(MTEngine):
    """Yandex Translate API."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Yandex API ключ не указан")
        self.api_key = api_key
    
    def translate(self, text: str, source_lang: str = "ru", target_lang: str = "en") -> str:
        """Перевести текст через Yandex Translate."""
        try:
            import requests
            
            url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
            params = {
                'key': self.api_key,
                'text': text,
                'lang': f'{source_lang}-{target_lang}'
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            if 'text' in result and result['text']:
                return ' '.join(result['text'])
            else:
                raise Exception("Пустой ответ от Yandex API")
        except Exception as e:
            raise Exception(f"Ошибка перевода Yandex: {e}")


def get_mt_engine(engine_name: str = None, glossary_id: str = None) -> MTEngine:
    """
    Получить экземпляр MT движка.
    
    Args:
        engine_name: Название движка (deepl, google, yandex)
        glossary_id: ID глоссария DeepL (опционально, только для DeepL)
        
    Returns:
        Экземпляр MTEngine
    """
    engine_name = engine_name or config.DEFAULT_MT_ENGINE
    
    if engine_name.lower() == "deepl":
        return DeepLEngine(config.DEEPL_API_KEY, glossary_id=glossary_id)
    elif engine_name.lower() == "google":
        return GoogleTranslateEngine(config.GOOGLE_API_KEY, config.GOOGLE_PROJECT_ID)
    elif engine_name.lower() == "yandex":
        return YandexTranslateEngine(config.YANDEX_API_KEY)
    else:
        raise ValueError(f"Неизвестный MT движок: {engine_name}")

