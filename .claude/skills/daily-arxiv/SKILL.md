---
name: daily-arxiv
description: Запуск или управление ежедневной лентой рекомендаций arXiv. Используется для разовых рекомендаций новых статей, настройки/статуса/отключения запланированного GitHub Actions, дайджестов по электронной почте и явной авто-загрузки с высокой уверенностью через /ingest.
argument-hint: "[setup|status|disable] [--mode inform|auto-ingest] [--hours 24] [--categories <cat...>] [--max-recommendations 10] [--max-auto-ingest 1] [--send-email true|false]"
---

# /daily-arxiv

> Запуск или управление ежедневной лентой рекомендаций статей. Голый `/daily-arxiv` означает "запустить сегодняшний проход рекомендаций сейчас"; GitHub Actions — это лишь ненаблюдаемый планировщик для того же пайплайна.

Загружайте справочники только при необходимости:

- `references/recommendation-and-ingest-policy.md` — доказательства, схема решений LLM, порог уверенности и ограничения авто-загрузки
- `references/automation-scaffold.md` — поведение настройки/статуса GitHub Actions, секреты, артефакты и режимы отказа

## Команды

- `/daily-arxiv`: запустить разовый проход рекомендаций сейчас. Если `config/daily-arxiv.yml` отсутствует, определите параметры по умолчанию из wiki и продолжите.
- `/daily-arxiv setup`: создайте или восстановите `config/daily-arxiv.yml` из `config/daily-arxiv.yml.example`; убедитесь, что `.github/workflows/daily-arxiv.yml` существует и что блок `env:` задачи `daily-arxiv:` содержит `SEMANTIC_SCHOLAR_API_KEY` и `DEEPXIV_TOKEN` — **добавьте отсутствующие строки автоматически** вместо того, чтобы просить пользователя вручную редактировать YAML; и объясните необходимые секреты. См. *Настройка* ниже для точной процедуры патча.
- `/daily-arxiv status`: проверка конфигурации, наличия workflow, расписания, режима, доступности API/почтовых секретов и недавних артефактов при наличии.
- `/daily-arxiv disable`: установите `schedule.enabled: false` в конфигурации или подскажите пользователю, что изменить; ручной `/daily-arxiv` по-прежнему должен работать.

> При запуске `setup` или `status` относитесь к секретам S2/DeepXiv как обязательным (не опциональным) для любого пайплайна с дневной частотой и направьте пользователя в [`docs/daily-arxiv-deployment.md`](../../../docs/daily-arxiv-deployment.md) для полного контрольного списка настройки и поиска неисправностей по симптомам.

## Входы

- `--mode inform|auto-ingest`: по умолчанию `inform`. Никогда не выводите `auto-ingest` из состояния репозитория.
- `--hours N`: извлекайте статьи за последние N часов; конфигурация/по умолчанию — 24.
- `--categories <cat...>`: переопределите настроенные категории arXiv.
- `--max-recommendations N`: максимальное количество статей в дайджесте; конфигурация/по умолчанию — 10.
- `--max-auto-ingest N`: лимит для авто-загрузки с высокой уверенностью; конфигурация/по умолчанию — 1.
- `--send-email true|false`: предпочтение workflow/настройки для SMTP-доставки.

## Процесс настройки

Запускается через `/daily-arxiv setup`. Идемпотентен — повторный запуск на исправном репозитории не выполняет действий.

1. **Конфигурация**: если `config/daily-arxiv.yml` отсутствует, скопируйте из `config/daily-arxiv.yml.example`. Если присутствует, не трогайте (предпочтения пользователя сохраняются).

2. **Файл workflow**: убедитесь, что `.github/workflows/daily-arxiv.yml` существует. Если отсутствует, направьте пользователя в `docs/daily-arxiv-deployment.md` и остановитесь — воссоздание workflow с нуля не входит в phạmх настройки.

3. **Экспозиции переменных окружения workflow (автопатч)**: в `.github/workflows/daily-arxiv.yml` найдите блок `env:` задачи `daily-arxiv:`. Убедитесь, что обе строки присутствуют какsiblings `HAS_CLAUDE_CODE_AUTH`:

   ```yaml
   SEMANTIC_SCHOLAR_API_KEY: ${{ secrets.SEMANTIC_SCHOLAR_API_KEY }}
   DEEPXIV_TOKEN:            ${{ secrets.DEEPXIV_TOKEN }}
   ```

   - Если обе строки уже есть, не делайте ничего.
   - Если не хватает одной, добавьте отсутствующую строку.
   - Если блок `env:` вообще отсутствует (старый workflow), вставьте его под задачей с обеими строками и существующими флагами `HAS_CLAUDE_CODE_AUTH` / `HAS_REVIEW_LLM`. Не трогайте другие шаги.
   - После любого патча сообщите пользователю, что изменено, и напомните сделать коммит.

4. **Проверка секретов**: перечислите, какие из `ANTHROPIC_API_KEY` или `CLAUDE_CODE_OAUTH_TOKEN`, `SEMANTIC_SCHOLAR_API_KEY`, `DEEPXIV_TOKEN` и опциональных SMTP-секретов настроены. Используйте `gh secret list` при доступности; иначе инструктируйте пользователя запустить его. Покажите отсутствующие обязательные секреты с точной командой `gh secret set`.

5. **Сводка**: отчёт о том, что создано, исправлено и что пользователю ещё предстоит сделать (установить GitHub App, задать отсутствующие секреты, проверить одной командой `gh workflow run daily-arxiv.yml`).

## Процесс запуска

1. Определите интерпретатор Python и запустите детерминированную подготовку:

   ```bash
   python3 tools/daily_arxiv.py prepare --wiki-root wiki --out .daily-arxiv/run/recommendation-context.json --out-feed .daily-arxiv/run/feed.json
   ```

2. Прочитайте `.daily-arxiv/run/recommendation-context.json`. Оцените кандидатов с помощью LLM, используя предоставленные доказательства arXiv, wiki, Semantic Scholar и DeepXiv. Запишите `.daily-arxiv/run/llm-decisions.json` с полями `decision`, `confidence`, `score`, `rationale`, `wiki_connections` и `signals_used`. В режиме CI inform review LLM, совместимый с OpenAI, может делать это через:

   ```bash
   python3 tools/daily_arxiv.py recommend-llm --context .daily-arxiv/run/recommendation-context.json --out .daily-arxiv/run/llm-decisions.json
   ```

3. Если режим — `auto-ingest`, используйте только Claude Code runtime: выберите `decision: ingest` + `confidence: high`, соблюдайте `max_auto_ingest` и вызывайте `/ingest <arxiv-url>` последовательно. Не записывайте вручную файлы wiki или графа. Сторонние LLM — только для рекомендаций и не должны выполнять авто-загрузку.

4. Финализируйте дайджест:

   ```bash
   python3 tools/daily_arxiv.py finalize --context .daily-arxiv/run/recommendation-context.json --decisions .daily-arxiv/run/llm-decisions.json --out-md .daily-arxiv/run/digest.md --out-json .daily-arxiv/run/digest.json
   ```

5. Отчитайтесь о сильных рекомендациях, возможно интересных статьях, пропущенных дубликатах, деградировавших сигналах, результатах авто-загрузки и подсказках по настройке/статусу.

## Взаимодействие с Wiki

Читает `wiki/index.md`, `wiki/papers/`, `wiki/topics/`, `wiki/concepts/`, `wiki/methods/`, `wiki/ideas/` и `wiki/log.md` для построения профиля интересов и дедупликации кандидатов.

Записывает только файлы в `.daily-arxiv/` во время информационных запусков. В режиме `auto-ingest` все устойчивые мутации wiki/raw должны поступать из `/ingest`.

## Связи

- `/discover` отвечает на запросы о том, что читать дальше, от якорей, тем или состояния wiki; никогда не загружает.
- `/daily-arxiv` отслеживает свежий поток arXiv и может уведомлять ежедневно или вручную.
- `/ingest` — единственный путь включения статей. `/daily-arxiv` может вызывать его только в явном режиме `auto-ingest`.
