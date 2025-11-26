#!/bin/bash

# Скрипт для настройки GitHub репозитория
# Использование: ./setup_github.sh YOUR_GITHUB_USERNAME REPO_NAME

set -e

GITHUB_USERNAME=$1
REPO_NAME=$2

if [ -z "$GITHUB_USERNAME" ] || [ -z "$REPO_NAME" ]; then
    echo "Использование: ./setup_github.sh YOUR_GITHUB_USERNAME REPO_NAME"
    echo "Пример: ./setup_github.sh yury book-translator"
    exit 1
fi

echo "🚀 Настройка GitHub репозитория..."
echo ""

# Проверка, инициализирован ли git
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
else
    echo "✓ Git репозиторий уже инициализирован"
fi

# Проверка наличия коммитов
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "📝 Создание первого коммита..."
    git add .
    git commit -m "Initial commit: Book translation system (RU → EN)"
else
    echo "✓ Коммиты уже существуют"
fi

# Проверка наличия remote
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️  Remote 'origin' уже настроен:"
    git remote get-url origin
    read -p "Перезаписать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Отмена. Remote не изменен."
        exit 0
    fi
fi

# Добавление remote
GITHUB_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
echo "🔗 Добавление remote: ${GITHUB_URL}"
git remote add origin "$GITHUB_URL"

# Переименование ветки в main (если нужно)
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🌿 Переименование ветки в 'main'..."
    git branch -M main
fi

echo ""
echo "✅ Локальный репозиторий настроен!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Создайте репозиторий на GitHub: https://github.com/new"
echo "   - Имя: ${REPO_NAME}"
echo "   - НЕ добавляйте README, .gitignore, license (они уже есть)"
echo ""
echo "2. После создания репозитория выполните:"
echo "   git push -u origin main"
echo ""
echo "3. Для работы с ChatGPT используйте ссылку:"
echo "   https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"

