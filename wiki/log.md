# Wiki Log

Хронологический журнал изменений LLM-Wiki.

## [2026-05-20] ingest | ГОСТ 31937-2024

- Добавлен 1 новый источник в `raw/`: ГОСТ 31937-2024 (полный текст, ~2400 строк, Контур.Норматив).
- Создана страница [[ГОСТ 31937-2024]]: область применения, категории технического состояния, обследование, мониторинг, периодичность, структура стандарта.
- Обновлены [[Source Notes]] (секция «Строительство и нормативы») и [[index]].
- Остальные 9 ранее ingested источников без изменений; неполный Habr-clip по Zettelkasten — без изменений.

## [2026-05-20] ingest | Reconciliation — no new sources

- Запрошен ingest всего `raw/`: сверка с [[Source Notes]] и файловой системой.
- В `raw/` — 9 файлов; все уже ingested (последний полный ingest — 2026-05-04).
- Новых, удалённых и изменённых raw-источников не обнаружено; `wiki/` не менялся.
- Напоминание: `raw/Zettelkasten и Obsidian ваш помощник в структурировании знаний.md` по-прежнему неполный — нужен повторный clip или другой источник.

## [2026-05-04] ingest | Initial raw folder bootstrap

- Processed 9 sources from `raw/` without modifying raw files.
- Created initial wiki map: [[index]].
- Created concept pages: [[LLM Wiki]], [[LLM Wiki Workflow]], [[LLM Wiki Lifecycle]], [[Obsidian]], [[Zettelkasten]], [[Second Brain]], [[PARA]], [[Obsidian Web Clipper]].
- Created source overview: [[Source Notes]].
- Noted quality issue: `raw/Zettelkasten и Obsidian ваш помощник в структурировании знаний.md` appears incomplete and contains almost no article body.
- No direct contradiction found; richer lifecycle/automation sources are treated as extensions of the minimal [[LLM Wiki]] pattern.

## [2026-05-04] maintenance | Added maintainer prompts

- Created `prompts/initial-llm-wiki-prompt.md` with the initial LLM-Wiki maintainer prompt.
- Created `prompts/raw-change-workflow-prompt.md` with the workflow for added or removed files in `raw/`.
- Updated `README.md` to document the `prompts/` directory.

## [2026-05-05] maintenance | Consolidated agent rules into AGENTS.md

- Создан `AGENTS.md` в корне репозитория как единый schema-файл с правилами для LLM-агента (соответствует рекомендации паттерна [[LLM Wiki]]).
- Удалены `prompts/initial-llm-wiki-prompt.md` и `prompts/raw-change-workflow-prompt.md`; их содержимое объединено в `AGENTS.md` (baseline + workflow при изменениях в `raw/`).
- Удалена пустая папка `prompts/`.
- Удалён `.cursor/rules/llm-wiki-maintenance.mdc` — Cursor подхватывает `AGENTS.md` нативно, отдельный rule-файл стал дубликатом.
- Обновлён `README.md`: раздел «Промпты» заменён на раздел «Schema для агента» со ссылкой на `AGENTS.md`.
- Обновлён [[index]]: закрыт открытый вопрос про необходимость schema-файла в пользу `AGENTS.md`; добавлена секция «Schema агента».
- Содержательных изменений в `wiki/`-страницах и в `raw/` нет.
