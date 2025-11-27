#!/usr/bin/env python3
"""
ChatGPT Agent для автоматизации работы с рекомендациями ChatGPT.

Этот агент:
1. Анализирует код через ChatGPT API
2. Получает рекомендации
3. Показывает их пользователю
4. Применяет изменения после одобрения
5. Коммитит и пушит автоматически
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from openai import OpenAI
from datetime import datetime

# Загружаем конфигурацию
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ Ошибка: OPENAI_API_KEY не найден в .env файле")
    sys.exit(1)


class ChatGPTAgent:
    """Агент для работы с ChatGPT API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key, timeout=120.0)
        self.project_root = Path(__file__).parent
        self.recommendations_file = self.project_root / "chatgpt_recommendations.json"
        
    def analyze_code(self, file_path: str = None, question: str = None) -> Dict:
        """
        Анализирует код через ChatGPT.
        
        Args:
            file_path: Путь к файлу для анализа (если None - анализирует весь проект)
            question: Вопрос или задача для ChatGPT
            
        Returns:
            Словарь с рекомендациями
        """
        print(f"\n🤖 Анализирую код через ChatGPT...")
        
        # Читаем код
        if file_path:
            code_content = self._read_file(file_path)
            context = f"Файл: {file_path}\n\nКод:\n{code_content}"
        else:
            # Анализируем ключевые файлы проекта
            key_files = [
                "translator.py",
                "llm_post_editor.py",
                "mt_engines.py",
                "main.py"
            ]
            context = "Структура проекта:\n"
            for file in key_files:
                file_path_obj = self.project_root / file
                if file_path_obj.exists():
                    context += f"\n--- {file} ---\n"
                    context += self._read_file(str(file_path_obj))
                    context += "\n"
        
        # Формируем промпт
        prompt = f"""Ты - опытный Python разработчик и архитектор. Проанализируй код и дай рекомендации.

{context}

{"\nВопрос/Задача: " + question if question else "\nПроанализируй код и предложи улучшения:"}

Твоя задача:
1. Найди потенциальные проблемы
2. Предложи улучшения кода
3. Предложи оптимизации
4. Укажи на лучшие практики

Формат ответа (JSON):
{{
    "summary": "Краткое резюме анализа",
    "issues": [
        {{
            "file": "путь/к/файлу.py",
            "line": 42,
            "severity": "high|medium|low",
            "type": "bug|performance|style|security",
            "description": "Описание проблемы",
            "recommendation": "Рекомендация по исправлению",
            "code_before": "старый код",
            "code_after": "новый код"
        }}
    ],
    "improvements": [
        {{
            "file": "путь/к/файлу.py",
            "description": "Описание улучшения",
            "code_before": "старый код",
            "code_after": "новый код",
            "reason": "Почему это улучшение"
        }}
    ],
    "general_recommendations": [
        "Общая рекомендация 1",
        "Общая рекомендация 2"
    ]
}}

Верни ТОЛЬКО валидный JSON, без дополнительного текста."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - опытный Python разработчик. Анализируй код и давай конкретные рекомендации в формате JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Пытаемся извлечь JSON из ответа
            json_text = self._extract_json(result_text)
            recommendations = json.loads(json_text)
            
            # Сохраняем рекомендации
            self._save_recommendations(recommendations)
            
            return recommendations
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
            print(f"Ответ ChatGPT:\n{result_text}")
            return {
                "summary": "Ошибка парсинга ответа",
                "raw_response": result_text,
                "issues": [],
                "improvements": [],
                "general_recommendations": []
            }
        except Exception as e:
            print(f"❌ Ошибка при обращении к ChatGPT API: {e}")
            return None
    
    def _read_file(self, file_path: str) -> str:
        """Читает файл."""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return f"Файл {file_path} не найден"
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            return f"Ошибка чтения файла: {e}"
    
    def _extract_json(self, text: str) -> str:
        """Извлекает JSON из текста."""
        # Ищем JSON блок
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            return text[start:end]
        
        return text
    
    def _save_recommendations(self, recommendations: Dict):
        """Сохраняет рекомендации в файл."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations
        }
        self.recommendations_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"💾 Рекомендации сохранены в {self.recommendations_file}")
    
    def display_recommendations(self, recommendations: Dict):
        """Красиво отображает рекомендации."""
        if not recommendations:
            print("❌ Нет рекомендаций для отображения")
            return
        
        print("\n" + "="*80)
        print("📋 РЕКОМЕНДАЦИИ ОТ CHATGPT")
        print("="*80)
        
        if "summary" in recommendations:
            print(f"\n📝 Резюме: {recommendations['summary']}")
        
        # Проблемы
        if "issues" in recommendations and recommendations["issues"]:
            print("\n🔴 ПРОБЛЕМЫ:")
            for i, issue in enumerate(recommendations["issues"], 1):
                severity_emoji = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(issue.get("severity", "medium"), "⚪")
                
                print(f"\n{i}. {severity_emoji} [{issue.get('severity', 'medium').upper()}] {issue.get('type', 'issue').upper()}")
                print(f"   Файл: {issue.get('file', 'unknown')}")
                if issue.get('line'):
                    print(f"   Строка: {issue.get('line')}")
                print(f"   Описание: {issue.get('description', 'Нет описания')}")
                print(f"   Рекомендация: {issue.get('recommendation', 'Нет рекомендации')}")
                
                if issue.get('code_before') and issue.get('code_after'):
                    print(f"\n   Было:")
                    print(f"   {issue['code_before']}")
                    print(f"\n   Станет:")
                    print(f"   {issue['code_after']}")
        
        # Улучшения
        if "improvements" in recommendations and recommendations["improvements"]:
            print("\n✨ УЛУЧШЕНИЯ:")
            for i, improvement in enumerate(recommendations["improvements"], 1):
                print(f"\n{i}. Файл: {improvement.get('file', 'unknown')}")
                print(f"   Описание: {improvement.get('description', 'Нет описания')}")
                print(f"   Причина: {improvement.get('reason', 'Нет причины')}")
                
                if improvement.get('code_before') and improvement.get('code_after'):
                    print(f"\n   Было:")
                    print(f"   {improvement['code_before']}")
                    print(f"\n   Станет:")
                    print(f"   {improvement['code_after']}")
        
        # Общие рекомендации
        if "general_recommendations" in recommendations and recommendations["general_recommendations"]:
            print("\n💡 ОБЩИЕ РЕКОМЕНДАЦИИ:")
            for i, rec in enumerate(recommendations["general_recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)
    
    def apply_recommendation(self, recommendation: Dict, auto_commit: bool = False) -> bool:
        """
        Применяет одну рекомендацию.
        
        Args:
            recommendation: Словарь с рекомендацией
            auto_commit: Автоматически коммитить изменения
            
        Returns:
            True если успешно применено
        """
        file_path = recommendation.get('file')
        if not file_path:
            print("❌ Не указан файл для изменения")
            return False
        
        full_path = self.project_root / file_path
        if not full_path.exists():
            print(f"❌ Файл {file_path} не найден")
            return False
        
        code_after = recommendation.get('code_after')
        if not code_after:
            print("❌ Нет нового кода для применения")
            return False
        
        # Читаем текущий файл
        current_content = full_path.read_text(encoding='utf-8')
        code_before = recommendation.get('code_before', '')
        
        # Заменяем код
        if code_before in current_content:
            new_content = current_content.replace(code_before, code_after)
            full_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Изменения применены в {file_path}")
            
            if auto_commit:
                self._commit_changes(file_path, recommendation.get('description', 'Apply ChatGPT recommendation'))
            
            return True
        else:
            print(f"⚠️ Не удалось найти код для замены в {file_path}")
            print(f"Искали:\n{code_before}")
            return False
    
    def _commit_changes(self, file_path: str, message: str):
        """Коммитит изменения."""
        try:
            subprocess.run(
                ["git", "add", file_path],
                cwd=self.project_root,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Apply ChatGPT recommendation: {message}"],
                cwd=self.project_root,
                check=True
            )
            print(f"💾 Изменения закоммичены: {message}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Ошибка при коммите: {e}")


def main():
    """Главная функция для интерактивного режима."""
    agent = ChatGPTAgent()
    
    print("🤖 ChatGPT Agent для автоматизации")
    print("="*80)
    
    # Парсим аргументы
    if len(sys.argv) > 1:
        if sys.argv[1] == "--analyze":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            question = sys.argv[3] if len(sys.argv) > 3 else None
            
            recommendations = agent.analyze_code(file_path, question)
            if recommendations:
                agent.display_recommendations(recommendations)
        elif sys.argv[1] == "--show":
            # Показываем последние рекомендации
            if agent.recommendations_file.exists():
                data = json.loads(agent.recommendations_file.read_text(encoding='utf-8'))
                agent.display_recommendations(data["recommendations"])
            else:
                print("❌ Нет сохраненных рекомендаций. Сначала запустите --analyze")
        else:
            print("Использование:")
            print("  python chatgpt_agent.py --analyze [файл] [вопрос]")
            print("  python chatgpt_agent.py --show")
    else:
        # Интерактивный режим
        print("\nВыберите действие:")
        print("1. Анализ всего проекта")
        print("2. Анализ конкретного файла")
        print("3. Показать последние рекомендации")
        print("4. Выход")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == "1":
            question = input("Вопрос/задача для ChatGPT (или Enter для общего анализа): ").strip()
            recommendations = agent.analyze_code(question=question or None)
            if recommendations:
                agent.display_recommendations(recommendations)
                
                # Предлагаем применить изменения
                apply = input("\nПрименить рекомендации? (y/n): ").strip().lower()
                if apply == 'y':
                    # Здесь можно добавить интерактивное применение
                    print("💡 Для применения используйте рекомендации из файла chatgpt_recommendations.json")
        
        elif choice == "2":
            file_path = input("Путь к файлу: ").strip()
            question = input("Вопрос/задача (или Enter): ").strip()
            recommendations = agent.analyze_code(file_path, question=question or None)
            if recommendations:
                agent.display_recommendations(recommendations)
        
        elif choice == "3":
            if agent.recommendations_file.exists():
                data = json.loads(agent.recommendations_file.read_text(encoding='utf-8'))
                agent.display_recommendations(data["recommendations"])
            else:
                print("❌ Нет сохраненных рекомендаций")


if __name__ == "__main__":
    main()

