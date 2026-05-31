---
description: 'Ответ рецензентам (файл) [--paper-slug SLUG] [--venue VENUE] [--stress-test] [--format formal|rich]'
---

Подготовь ответ на рецензию, используя скилл `rebuttal`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Где файл с рецензией? Укажи путь или slug статьи»

## Флаги

- `--paper-slug <slug>` — slug статьи (для привязки ответа к статье)
- `--venue <VENUE>` — издание/конференция (влияет на формат ответа)
- `--stress-test` — провести стресс-тест аргументов (tools/stress_test.py)
- `--format` — формат ответа:
  - `formal` (по умолчанию) — строгий академический формат
  - `rich` — расширенный формат с дополнительными пояснениями

## Примеры

```
/rebuttal reviews/neurips-2024/review1.md
/rebuttal reviews/neurips-2024/review1.md --paper-slug my-paper --venue NeurIPS
/rebuttal reviews/neurips-2024/review1.md --stress-test --format rich
```

Порядок действий:
1. Если файл пустой — спроси у пользователя путь или slug
2. Определи флаги
3. Вызови скилл `rebuttal` с файлом и флагами
