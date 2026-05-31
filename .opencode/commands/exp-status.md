---
description: 'Статус экспериментов [--pipeline SLUG] [--collect-ready] [--auto-advance]'
---

Покажи статус экспериментов, используя скилл `exp-status`.

Аргументы: $ARGUMENTS

## Флаги

- `--pipeline <slug>` — показать статус только для указанного пайплайна
- `--collect-ready` — показать эксперименты, готовые к сбору результатов
- `--auto-advance` — автоматически продвинуть эксперименты на следующий этап

## Примеры

```
/exp-status
/exp-status --pipeline research-2024
/exp-status --collect-ready
/exp-status --auto-advance
```

Порядок действий:
1. Определи флаги из аргументов
2. Вызови скилл `exp-status` с флагами
