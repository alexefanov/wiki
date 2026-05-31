---
description: 'Улучшение (артефакт) [--max-rounds N] [--target-score N] [--difficulty standard|hard|adversarial] [--focus method|evidence|writing|completeness]'
---

Улучши научный артефакт, используя скилл `refine`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какой артефакт улучшать? Укажи путь или slug»

## Флаги

- `--max-rounds N` — максимальное количество раундов улучшения
- `--target-score N` — целевой评分 (tools/refine.py)
- `--difficulty` — уровень сложности проверки:
  - `standard` (по умолчанию) — стандартная проверка
  - `hard` — жёсткая проверка
  - `adversarial` — агрессивная проверка на слабые места
- `--focus` — область фокуса улучшения:
  - `method` — методология
  - `evidence` — доказательная база
  - `writing` — качество текста
  - `completeness` — полнота

## Примеры

```
/refine papers/my-article
/refine papers/my-article --max-rounds 3 --target-score 8
/refine papers/my-article --difficulty hard --focus method
/refine my-paper --focus writing --max-rounds 2
```

Порядок действий:
1. Если артефакт пустой — спроси у пользователя
2. Определи флаги
3. Вызови скилл `refine` с артефактом и флагами
