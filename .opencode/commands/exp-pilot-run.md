---
description: 'Пилотный запуск (idea-slug) [--env local|remote]'
---

Запусти пилотный эксперимент, используя скилл `exp-pilot-run`.

Аргументы: $ARGUMENTS

Если аргументы пусты — спроси пользователя:
- «Какую идею запускать? Укажи slug»

## Флаги

- `--env` — среда выполнения:
  - `local` (по умолчанию) — на локальной машине
  - `remote` — на удалённом сервере (tools/remote.py)

## Примеры

```
/exp-pilot-run transformer-transfer
/exp-pilot-run transformer-transfer --env remote
```

Порядок действий:
1. Если slug пустой — спроси у пользователя
2. Определи флаг --env
3. Вызови скилл `exp-pilot-run` с slug и средой
