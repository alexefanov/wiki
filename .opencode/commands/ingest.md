---
description: 'Загрузка документа в wiki (путь/URL) [--discover] [--visualize]'
---

Загрузи документ в базу знаний, используя скилл `ingest`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какой документ загружать? Укажи путь к файлу или URL»

## Флаги

- `--discover` — после загрузки найти похожие статьи (tools/discover.py)
- `--visualize` — после загрузки обновить визуализ графа (tools/research_wiki.py --visualize)

## Примеры

```
/ingest raw/papers/example.pdf
/ingest https://arxiv.org/abs/2401.12345
/ingest raw/papers/example.pdf --discover --visualize
/ingest https://arxiv.org/pdf/2401.12345 --discover
```

Порядок действий:
1. Если источник пустой — спроси у пользователя путь или URL
2. Определи флаги
3. Вызови скилл `ingest` с источником и флагами
