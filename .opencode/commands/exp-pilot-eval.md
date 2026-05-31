---
description: 'Оценка пилота (idea-slug) [--auto]'
---

Оцени результаты пилотного запуска, используя скилл `exp-pilot-eval`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какую идею оценивать? Укажи slug»

## Флаги

- `--auto` — автоматическая оценка без участия пользователя

## Примеры

```
/exp-pilot-eval transformer-transfer
/exp-pilot-eval transformer-transfer --auto
```

Порядок действий:
1. Если slug пустой — спроси у пользователя
2. Определи флаг --auto
3. Вызови скилл `exp-pilot-eval` с slug и флагом
