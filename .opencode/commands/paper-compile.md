---
description: 'Компиляция LaTeX (каталог) [--fix] [--checklist]'
---

Скомпилируй статью из LaTeX, используя скилл `paper-compile`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «В каком каталоге находится статья?»

## Флаги

- `--fix` — автоматически исправить ошибки компиляции
- `--checklist` — показать чеклист перед компиляцией (tools/paper_compile.py --checklist)

## Примеры

```
/paper-compile papers/my-article
/paper-compile papers/my-article --fix
/paper-compile papers/my-article --checklist
```

Порядок действий:
1. Если каталог пустой — спроси у пользователя
2. Определи флаги
3. Вызови скилл `paper-compile` с каталогом и флагами
