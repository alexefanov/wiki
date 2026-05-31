---
description: 'Проверка (артефакт) [--difficulty standard|hard|adversarial] [--focus method|evidence|writing|completeness]'
---

Проверь научный артефакт, используя скилл `review`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какой артефакт проверять? Укажи путь или slug»

## Флаги

- `--difficulty` — уровень сложности проверки:
  - `standard` (по умолчанию) — стандартная проверка
  - `hard` — жёсткая проверка
  - `adversarial` — агрессивная проверка на слабые места
- `--focus` — область фокуса проверки:
  - `method` — методология
  - `evidence` — доказательная база
  - `writing` — качество текста
  - `completeness` — полнота

## Примеры

```
/review papers/my-article
/review papers/my-article --difficulty hard --focus method
/review my-paper --focus writing
/review papers/my-article --difficulty adversarial --focus evidence
```

Порядок действий:
1. Если артефакт пустой — спроси у пользователя
2. Определи флаги
3. Вызови скилл `review` с артефактом и флагами
