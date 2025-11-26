"""
Модуль для пост-редактирования перевода через LLM.
"""

from typing import Optional
import config


class LLMPostEditor:
    """Базовый класс для LLM пост-редакторов."""
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать перевод."""
        raise NotImplementedError
    
    def _create_prompt(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Создать промпт для пост-редактирования."""
        glossary_text = ""
        if glossary:
            glossary_items = "\n".join([f"- {k}: {v}" for k, v in glossary.items()])
            glossary_text = f"\n\nГлоссарий для консистентности:\n{glossary_items}"
        
        prompt = f"""You are a professional literary translator specializing in Russian to American English translation. Your task is to post-edit a machine-translated text to make it sound natural, fluent, and native-like.

Guidelines:
1. Preserve the original meaning and tone
2. Make the translation sound natural and idiomatic in American English
3. Maintain the emotional tone and style of the original
4. Fix any awkward phrasings, literal translations, or grammatical errors
5. Ensure consistency with the glossary terms provided
6. Preserve dialogue style and character voice
7. Keep the narrative flow and pacing

Original Russian text:
{original_text}

Machine-translated English text:
{translated_text}
{glossary_text}

Please provide the improved, natural-sounding English translation. Return only the translated text without any explanations or comments."""
        
        return prompt


class GPT4PostEditor(LLMPostEditor):
    """GPT-4 для пост-редактирования."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API ключ не указан")
        self.api_key = api_key
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать через GPT-4."""
        try:
            from openai import OpenAI
            # Создаем клиент без дополнительных параметров для совместимости
            client = OpenAI(api_key=self.api_key, timeout=60.0)
            
            prompt = self._create_prompt(original_text, translated_text, glossary)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Используем GPT-4o для лучшего качества
                messages=[
                    {"role": "system", "content": "You are a professional literary translator specializing in Russian to American English translation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Ошибка пост-редактирования GPT-4: {e}")


class ClaudePostEditor(LLMPostEditor):
    """Claude (Anthropic) для пост-редактирования."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Anthropic API ключ не указан")
        self.api_key = api_key
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать через Claude."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            prompt = self._create_prompt(original_text, translated_text, glossary)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=config.LLM_MAX_TOKENS,
                temperature=config.LLM_TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Ошибка пост-редактирования Claude: {e}")


class DeepSeekPostEditor(LLMPostEditor):
    """DeepSeek для пост-редактирования."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("DeepSeek API ключ не указан")
        self.api_key = api_key
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать через DeepSeek."""
        try:
            from openai import OpenAI
            # DeepSeek использует OpenAI-совместимый API
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com",
                timeout=60.0
            )
            
            prompt = self._create_prompt(original_text, translated_text, glossary)
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a professional literary translator specializing in Russian to American English translation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Ошибка пост-редактирования DeepSeek: {e}")


class CrokPostEditor(LLMPostEditor):
    """Crok для пост-редактирования."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Crok API ключ не указан")
        self.api_key = api_key
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать через Crok."""
        try:
            import requests
            
            prompt = self._create_prompt(original_text, translated_text, glossary)
            
            # Crok API endpoint (может потребоваться уточнение)
            url = "https://api.crok.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "crok-ai",
                "messages": [
                    {"role": "system", "content": "You are a professional literary translator specializing in Russian to American English translation."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": config.LLM_TEMPERATURE,
                "max_tokens": config.LLM_MAX_TOKENS
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise Exception(f"Ошибка пост-редактирования Crok: {e}")


class GrokPostEditor(LLMPostEditor):
    """Grok (xAI) для пост-редактирования."""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Grok API ключ не указан")
        self.api_key = api_key
    
    def post_edit(self, original_text: str, translated_text: str, glossary: dict = None) -> str:
        """Пост-редактировать через Grok."""
        try:
            from openai import OpenAI
            # Grok использует OpenAI-совместимый API
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
                timeout=60.0
            )
            
            prompt = self._create_prompt(original_text, translated_text, glossary)
            
            response = client.chat.completions.create(
                model="grok-beta",  # или "grok-2" в зависимости от доступных моделей
                messages=[
                    {"role": "system", "content": "You are a professional literary translator specializing in Russian to American English translation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Ошибка пост-редактирования Grok: {e}")


def get_llm_editor(editor_name: str = None) -> LLMPostEditor:
    """
    Получить экземпляр LLM пост-редактора.
    
    Args:
        editor_name: Название редактора (gpt4, claude, deepseek, crok)
        
    Returns:
        Экземпляр LLMPostEditor
    """
    editor_name = editor_name or config.DEFAULT_LLM_ENGINE
    
    if editor_name.lower() == "gpt4":
        return GPT4PostEditor(config.OPENAI_API_KEY)
    elif editor_name.lower() == "claude":
        return ClaudePostEditor(config.ANTHROPIC_API_KEY)
    elif editor_name.lower() == "deepseek":
        return DeepSeekPostEditor(config.DEEPSEEK_API_KEY)
    elif editor_name.lower() == "crok":
        return CrokPostEditor(config.CROK_API_KEY)
    elif editor_name.lower() == "grok":
        return GrokPostEditor(config.GROK_API_KEY)
    else:
        raise ValueError(f"Неизвестный LLM редактор: {editor_name}")

