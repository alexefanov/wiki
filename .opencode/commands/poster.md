---
description: 'Постер (статья) [--review] [--anonymous] [--no-figures] [--no-logos] [--no-refine]'
---

Создай академический постер, используя скилл `poster`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Из какой статьи делать постер? Укажи путь или slug»

## Флаги

- `--review` — показать постер перед сохранением для ревью
- `--anonymous` — анонимный режим (без авторов и affiliations, для double-blind)
- `--no-figures` — не включать фигуры
- `--no-logos` — не включать логотипы
- `--no-refine` — пропустить этап улучшения (tools/refine.py)

## Примеры

```
/poster papers/my-article
/poster papers/my-article --review
/poster papers/my-article --anonymous --no-logos
/poster papers/my-article --no-figures --no-refine
```

Порядок действий:
1. Если источник пустой — спроси у пользователя
2. Определи флаги
3. Вызови скилл `poster` с источником и флагами
