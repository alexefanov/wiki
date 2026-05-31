---
description: 'Лента arXiv [setup|status|disable] [--mode inform|auto-ingest] [--hours N] [--categories ...]'
---

Управление лентой arXiv, используя скилл `daily-arxiv`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Что сделать с лентой arXiv? (status / setup / disable)»

## Действия

- `status` — показать текущий статус ленты и последний дайджест
- `setup` — настроить ленту (категории, частота, email)
- `disable` — отключить автоматическую обработку

## Флаги

- `--mode` — режим работы:
  - `inform` (по умолчанию) — только информирование, без автозагрузки
  - `auto-ingest` — автоматическая загрузка подходящих статей в wiki
- `--hours N` — проверять статьи за последние N часов (по умолчанию 24)
- `--categories` — список категорий arXiv через запятую (cs.AI, cs.CL, cs.CV и т.д.)
- `--max-recommendations N` — максимальное количество рекомендаций в дайджесте
- `--max-auto-ingest N` — максимальное количество автоматических загрузок за запуск
- `--send-email true|false` — отправлять ли дайджест по email

## Примеры

```
/daily-arxiv status
/daily-arxiv setup --mode auto-ingest --hours 48
/daily-arxiv disable
/daily-arxiv --categories cs.AI,cs.CL --max-recommendations 5
```

Порядок действий:
1. Определи действие (setup/status/disable) из аргументов
2. Определи флаги
3. Если действие не указано — спроси у пользователя
4. Вызови скилл `daily-arxiv` с действием и флагами
