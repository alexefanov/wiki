---
description: 'План статьи (идеи) --venue VENUE [--title TITLE]'
---

Составь план статьи, используя скилл `paper-plan`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какие идеи включить в план? Укажи slug'ы через пробел»
- «В какое издание? (--venue обязателен)»

## Обязательные флаги

- `--venue <VENUE>` — целевое издание/конференция (ICLR, NeurIPS, ICML, ACL, CVPR, IEEE)

## Необязательные флаги

- `--title <TITLE>` — рабочее название статьи

## Примеры

```
/paper-plan idea-1 idea-2 --venue ICLR
/paper-plan transformer-transfer --venue NeurIPS --title "Transfer Learning for Defect Detection"
/paper-plan idea-1 idea-2 idea-3 --venue CVPR
```

Порядок действий:
1. Если идеи пустые — спроси slug'ы у пользователя
2. Если --venue не указан — спроси издание
3. Вызови скилл `paper-plan` с идеями, изданием и заголовком
