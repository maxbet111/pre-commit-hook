#!/bin/bash

# Шлях до хука в локальному проекті
HOOK_DEST=".git/hooks/pre-commit"
# Пряме посилання на ваш скрипт у GitHub (замініть YOUR_USER на ваш нікнейм)
RAW_URL="https://raw.githubusercontent.com/YOUR_USER/pre-commit-hook/main/pre-commit.py"

echo "📥 Завантаження Gitleaks pre-commit hook..."
curl -sSL "$RAW_URL" -o "$HOOK_DEST"

if [ $? -eq 0 ]; then
    chmod +x "$HOOK_DEST"
    echo "✅ Хук успішно завантажено до $HOOK_DEST"
    
    # Автоматичне ввімкнення через git config
    git config hooks.gitleaks.enabled true
    echo "⚙️  Перевірку gitleaks активовано (git config hooks.gitleaks.enabled true)"
else
    echo "❌ Помилка завантаження. Перевірте посилання або інтернет-з'єднання."
    exit 1
fi