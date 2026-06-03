---
name: init
description: Загрузка ΩmegaWiki из пользовательских источников с опциональным обнаружением, затем параллельная загрузка финального набора статей
argument-hint: "[topic] [--no-introduction]"
---

# /init

> Построение wiki из `raw/` с детерминированной подготовкой источников, управляемым планировщиком обнаружением, временными заметками/веб-каркасом и параллельным распределением/слиянием `/ingest`.

Используйте эти локальные справочники по мере необходимости:

- `references/prepare-and-discovery.md` — процесс подготовки, финальный выбор, получение и правила манифеста источников
- `references/planner-policy.md` — поведение планировщика и ожидания обрезки LLM
- `references/parallel-ingest.md` — изоляция worktree, контракт промпта подагента, слияние и очистка

## Входы

- `topic` (опционально): ключевые слова направления исследований; опускайте, когда `raw/` уже определяет начальный набор
- `--no-introduction` (опционально): отключение внешнего обнаружения; используйте только когда пользователь явно запрашивает
- Источники пользователя в `raw/papers/`, `raw/notes/`, `raw/web/`

## Выходы

- Каркас `wiki/` и временные страницы (Summary, темы, идеи, концепции)
- Подготовленные источники в `raw/tmp/` и `raw/discovered/`
- Финальные страницы статей через параллельные подагенты `/ingest`
- Манифесты `.checkpoints/init-*.json` для возобновления и повтора
- Обновлённые `wiki/index.md`, `wiki/log.md`, `wiki/graph/*`
- Обновлённые артефакты визуализации: `wiki/.obsidian/graph.json` и `wiki/canvases/*.canvas`

## Взаимодействие с Wiki

### Чтение

- `raw/papers/`, `raw/notes/`, `raw/web/`
- `.checkpoints/init-prepare.json` и `.checkpoints/init-sources.json` для возобновления, планирования и fan-out
- `wiki/index.md` плюс существующие `wiki/topics/`, `wiki/ideas/`, `wiki/concepts/`, `wiki/methods/` для избежания дублирования

### Запись

- Каркас `wiki/` и временные страницы
- `raw/tmp/` и `raw/discovered/`
- `wiki/index.md`, `wiki/log.md`, `wiki/graph/*`
- `.checkpoints/init-prepare.json`, `.checkpoints/init-plan.json`, `.checkpoints/init-sources.json`

### Создаваемые графовые рёбра

- `/init` сам создаёт только рёбра каркасного уровня, когда временные страницы требуют их
- все рёбра, управляемые статьями, делегируются `/ingest`

## Рабочий процесс

**Предусловие**: рабочая директория — корень проекта, содержащий `wiki/`, `raw/` и `tools/`. Установите `WIKI_ROOT=wiki/`. Определите `PYTHON_BIN` один раз и переиспользуйте для каждой команды Python во время `/init`:

```bash
GIT_COMMON_DIR=$(git rev-parse --git-common-dir 2>/dev/null || true)
PROJECT_ROOT=""
if [ -n "$GIT_COMMON_DIR" ]; then
  PROJECT_ROOT=$(cd "$(dirname "$GIT_COMMON_DIR")" 2>/dev/null && pwd)
fi

if   [ -x "$PROJECT_ROOT/.venv/bin/python" ];         then PYTHON_BIN="$PROJECT_ROOT/.venv/bin/python"
elif [ -x "$PROJECT_ROOT/.venv/Scripts/python.exe" ]; then PYTHON_BIN="$PROJECT_ROOT/.venv/Scripts/python.exe"
elif [ -x .venv/bin/python ];                         then PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ];                 then PYTHON_BIN=.venv/Scripts/python.exe
else                                                       PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Шаг 1: Инициализация структуры wiki

```bash
"$PYTHON_BIN" tools/research_wiki.py init wiki/
```

Создайте стандартные директории wiki, `graph/`, `outputs/`, `index.md` и `log.md`. Не добавляйте вторую запись init-журнала.

### Шаг 2: Подготовка локальных входов в `raw/tmp/`

```bash
"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --pdf-titles-json .checkpoints/init-pdf-titles.json --output-manifest .checkpoints/init-prepare.json
```

### Шаг 3: Планирование обнаружения, обрезка финального набора и запись манифеста источников

```bash
"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json
```

Затем запустите:
```bash
"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id> --id <candidate-id>
```

### Шаг 4: Создание каркасных страниц до загрузки статей

Создайте одну `wiki/Summary/{area}.md`, необходимые `wiki/topics/{slug}.md` и временные `ideas/`, `concepts/` и (опционально) `methods/` из notes/web.

Правила:
- notes/web авторитетны для намерений пользователя, а не для уверенности в литературе
- каждая страница, производная от notes/web, должна содержать эту точную строку сразу после frontmatter:

```markdown
Временная заметка: сформирована из raw/notes или raw/web во время /init; ожидает валидации из загруженных статей.
```

### Шаг 5: Параллельная загрузка статей с изоляцией worktree

Источники статей для этого шага строго из `.checkpoints/init-sources.json`.

Контракт параллельной загрузки:

- отложите несвязанные грязные файлы перед fan-out
- зафиксируйте свежесозданный каркас и init-манифесты перед fan-out
- проверьте `.gitattributes` для `merge=union`
- выполняйте `/ingest` ровно для одного переданного пути источника
- в РЕЖИМЕ INIT потребляйте переданный канонический путь точно как есть
- пропустите `fetch_s2.py citations`, `fetch_s2.py references`
- пропустите per-subagent `rebuild-index`, `rebuild-context-brief`, `rebuild-open-questions`
- зафиксируйте результат загрузки внутри worktree перед выходом

### Шаг 6: Слияние, пересборка и финальный отчёт

После завершения всех подагентов:

- последовательное слияние веток worktree на `BASE_BRANCH`
- консервативное разрешение конфликтов концепций/методов

```bash
"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/
"$PYTHON_BIN" tools/research_wiki.py dedup-citations wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/
"$PYTHON_BIN" tools/lint.py --wiki-dir wiki/ --fix
```

Затем обратное заполнение `cites` рёбер через Semantic Scholar.

Затем перегенерация артефактов визуализации.

## Ограничения

- Не выводите `--no-introduction` из состояния репозитория.
- `raw/papers/`, `raw/notes/` и `raw/web/` — входы пользователя
- `/init` может записывать внешние статьи только в `raw/discovered/`
- `/prefill` является опциональным фоновым заполнением и не является частью `/init`
- `/init` не должен создавать страницы `people/` напрямую
- Все загрузки статей должны выполняться через параллельные подагенты `/ingest` с изоляцией worktree

## Обработка ошибок

- **Нет парсимых статей в `raw/papers/`**: вход в режим bootstrap
- **`raw/notes/` и `raw/web/` пусты**: пропуск временного заполнения
- **Ошибка декодирования PDF**: сохраните локальный источник, запишите предупреждение
- **S2 или DeepXiv недоступны**: планировщик переходит на оставшиеся источники
- **Внешняя загрузка не удалась для одной статьи**: сохраните оставшийся финальный набор
- **Текущий чекаут — detached HEAD**: остановитесь перед worktree fan-out
- **stash pop не удался**: сохраните метаданные чекпоинта и сообщите
- **Пересборка визуализации не удалась**: предупредите и продолжите; никогда не завершайте `/init` с ошибкой

## Зависимости

### Инструменты (через Bash)
- `"$PYTHON_BIN" tools/research_wiki.py init wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-set-meta wiki/ init-session <key> <value>`
- `"$PYTHON_BIN" tools/research_wiki.py checkpoint-save/load/clear wiki/ init-session ...`
- `"$PYTHON_BIN" tools/research_wiki.py dedup-edges wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py dedup-citations wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-index wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py log wiki/ "<message>"`
- `"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"]`
- `"$PYTHON_BIN" tools/init_discovery.py prepare --raw-root raw --pdf-titles-json .checkpoints/init-pdf-titles.json --output-manifest .checkpoints/init-prepare.json`
- `"$PYTHON_BIN" tools/init_discovery.py plan [--topic "<topic>"] --mode auto --raw-root raw --wiki-root wiki --prepared-manifest .checkpoints/init-prepare.json --allow-introduction <true|false> --output-plan .checkpoints/init-plan.json`
- `"$PYTHON_BIN" tools/init_discovery.py fetch --raw-root raw --plan-json .checkpoints/init-plan.json --prepared-manifest .checkpoints/init-prepare.json --output-sources .checkpoints/init-sources.json --id <candidate-id>`
- `"$PYTHON_BIN" tools/lint.py --wiki-dir wiki/ --fix`
- `"$PYTHON_BIN" tools/visualize.py generate-obsidian-config wiki/`
- `"$PYTHON_BIN" tools/visualize.py generate-canvas wiki/`

### Навыки
- `/ingest` — одна статья на подагент, в РЕЖИМЕ INIT
- `/visualize` — Шаг 6 fan-out пересобирает группы цветов графа Obsidian, Canvas и HTML

### Внешние API, используемые init_discovery.py
- Semantic Scholar
- DeepXiv (опционально)
- эндпоинты загрузки arXiv
