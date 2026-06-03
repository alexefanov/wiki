---
name: ingest
description: Загрузка статьи в wiki — создание страниц (статьи + концепции + методы + люди) и построение всех перекрёстных ссылок и графовых рёбер. Запускайте, когда пользователь говорит "загрузить", "добавьте эту статью", сбрасывает `.pdf` / `.tex` / URL arXiv или просит включить статью в базу знаний.
argument-hint: <local-path-or-arXiv-URL> [--discover] [--visualize]
---

# /ingest

> Превращение одной статьи в полностью связанный набор wiki-страниц. Формирование корректных сущностей и правильных перекрёстных ссылок; семантические аудиты (симметрия обратных ссылок, висячие узлы, проверка значений полей) откладываются для `/check`.

Используйте эти локальные справочники по мере необходимости:

- `references/pdf-preprocessing.md` — восстановление arXiv-ID, получение tex, передача prepare-paper для прямых PDF
- `references/dedup-policy.md` — правило слияние-vs-создание для концепций и методов
- `references/cross-references.md` — матрица прямых/обратных ссылок и выбор типа ребра между статьями
- `references/init-mode.md` — передача из `/init` через манифест и соглашения параллельной безопасности
- `references/error-handling.md` — обработка ошибок парсинга, API и коллизий slug'ов

Откройте `runtime/schema/entities.yaml` для определений полей frontmatter и `runtime/templates/{kind}.md.tmpl` для структуры разделов тела. Для форматов `index.md`, `log.md` и `graph/` см. `runtime/schema/conventions.yaml` и `runtime/schema/edges.yaml`.

## Входы

- `source`: одно из — URL arXiv (например, `https://arxiv.org/abs/2106.09685`), локальный `.tex`, локальный `.pdf` или `canonical_ingest_path`, переданный из `/init` через `.checkpoints/init-sources.json` (см. `references/init-mode.md`)
- `--discover` (опционально, по умолчанию **выкл**): после финального отчёта вызовите `/discover --anchor <arxiv-id-этой-статьи>` и добавьте короткий список в отчёт как "Связанные статьи, которые вы, возможно, захотите загрузить дальше". Никогда не загружает автоматически. Пропускается в РЕЖИМЕ INIT. Считайте пользовательским флагом.
- `--visualize` (опционально, по умолчанию **выкл**): после пересборки шага 7 перегенерируйте артефакты визуализации Canvas через `tools/visualize.py generate-canvas`. Пропускается в РЕЖИМЕ INIT — родительский `/init` обрабатывает визуализацию один раз при слиянии.

## Выходы

- Одна полностью связанная страница статьи плюс связанные сущности (концепции, методы, люди)
- Графовые рёбра и цитаты, добавленные через `tools/research_wiki.py`
- Сводка в терминале с количеством страниц и предложенными дальнейшими загрузками

## Взаимодействие с Wiki

### Чтение

- `wiki/index.md` для существующих slug'ов и тегов
- `wiki/papers/*.md` для обнаружения уже загруженной статьи
- `wiki/concepts/*.md` и `wiki/foundations/*.md` для поиска дубликатов
- `wiki/methods/*.md` для поиска дубликатов существующих переиспользуемых методов
- `wiki/people/*.md` для существующих авторов
- `wiki/topics/*.md` для размещения статьи в существующих темах
- `wiki/graph/open_questions.md` для обнаружения случаев, когда статья затрагивает известный пробел

### Запись

- `wiki/papers/{slug}.md` — СОЗДАТЬ
- `wiki/concepts/{slug}.md` — СОЗДАТЬ (новая) или РЕДАКТИРОВАТЬ (добавить `key_papers`, aliases, варианты)
- `wiki/methods/{slug}.md` — СОЗДАТЬ (новая, только когда метод назван, переиспользуем и цитируем между статьями) или РЕДАКТИРОВАТЬ (добавить `source_papers`)
- `wiki/people/{slug}.md` — СОЗДАТЬ (importance ≥ 4 только) или РЕДАКТИРОВАТЬ (добавить в `## Recent work`)
- `wiki/topics/{slug}.md` — ТОЛЬКО РЕДАКТИРОВАТЬ (без CREATE из `/ingest`)
- `wiki/graph/edges.jsonl` — ДОПОЛНИТЬ через инструмент
- `wiki/graph/citations.jsonl` — ДОПОЛНИТЬ через инструмент
- `wiki/graph/context_brief.md` — ПЕРЕСОБРАТЬ (пропуск в РЕЖИМЕ INIT)
- `wiki/graph/open_questions.md` — ПЕРЕСОБРАТЬ (пропуск в РЕЖИМЕ INIT)
- `wiki/index.md` — ДОПОЛНИТЬ
- `wiki/log.md` — ДОПОЛНИТЬ через инструмент
- `wiki/canvases/*.canvas` — СОЗДАТЬ/ПЕРЕЗАПИСАТЬ (только при --visualize и не в РЕЖИМЕ INIT)

### Создаваемые графовые рёбра

- `paper → concept`: `introduces_concept` / `uses_concept` / `extends_concept` / `critiques_concept` с `confidence`
- `paper → foundation`: `derived_from` (foundation терминален; нет обратной ссылки)
- `paper → paper`: `same_problem_as` / `similar_method_to` / `builds_on` / `challenges` с `confidence`
- библиографическое `paper → paper`: `cites` в `graph/citations.jsonl`

## Рабочий процесс

**Предусловие**: рабочая директория содержит `wiki/`, `raw/` и `tools/`. Определите интерпретатор Python один раз и переиспользуйте:

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

### Шаг 1: Определение источника

1. Если `/init` передал `canonical_ingest_path`, войдите в **РЕЖИМ INIT** и используйте этот путь дословно. Не пересканируйте `raw/`. См. `references/init-mode.md`.
2. Если источник — URL arXiv, извлеките arXiv ID, используйте `"$PYTHON_BIN" tools/fetch_s2.py paper <arxiv-id>` для восстановления заголовка, затем запустите `"$PYTHON_BIN" tools/init_discovery.py download --raw-root raw --arxiv-id <arxiv-id> --title "<title-or-arxiv-id>"`.
3. Если источник — локальный `.tex`, используйте напрямую.
4. Если источник — локальный `.pdf`, запустите пайплайн предобработки из `references/pdf-preprocessing.md` для получения подготовленного `.tex` в `raw/tmp/`.

Правило постоянства raw: никогда не копируйте и не дублируйте файл, уже находящийся в `raw/discovered/`, `raw/tmp/` или `raw/papers/`, в другое поддерево raw.

### Шаг 2: Идентификация и обогащение статьи

1. Сгенерируйте slug статьи:
   ```bash
   "$PYTHON_BIN" tools/research_wiki.py slug "<заголовок-статьи>"
   ```
2. Проверка на существование: если `wiki/papers/{slug}.md` уже существует и arXiv ID или заголовок совпадают, сообщите и завершитесь.
3. Когда доступен arXiv ID, запросите Semantic Scholar:
   ```bash
   "$PYTHON_BIN" tools/fetch_s2.py paper <arxiv-id>
   ```
4. Опциональное обогащение DeepXiv, при доступности:
   ```bash
   "$PYTHON_BIN" tools/fetch_deepxiv.py brief <arxiv-id>
   "$PYTHON_BIN" tools/fetch_deepxiv.py head <arxiv-id>
   "$PYTHON_BIN" tools/fetch_deepxiv.py social <arxiv-id>
   ```

### Шаг 3: Запись страницы статьи

Откройте `runtime/schema/entities.yaml` (раздел papers) для набора полей и `runtime/templates/papers.md.tmpl` для порядка разделов тела. Заполните каждое обязательное поле frontmatter.

Три поля frontmatter, которые новая схема требует заполнить, хотя они не обязательны для lint:

- `tldr` — однострочное резюме статьи, подходящее как строка поиска/предварительного просмотра. НЕ многоабзачная аннотация; одно предложение.
- `contribution_type` — список типов вклада из замкнутого набора `[method, theory, benchmark, analysis, application, system, position, survey]`.
- `datasets` — список названий наборов данных/бенчмарков, используемых или вводимых статьёй.

Разделы тела для заполнения, в этом порядке: `Problem & Context`, `Key idea`, `Method`, `Experiment & Results`, `Limitations`, `Open questions`, `My take`, `Related`.

### Шаг 4: Концепции, методы, люди

Следуйте `references/dedup-policy.md`. Кратко:

1. Для каждого кандидата концепции сначала вызовите `find-similar-concept`.
2. Для каждого кандидата метода (названная, переиспользуемая техника) проверьте `wiki/methods/` по имени + тегам.
3. Предпочтите слияние с лучшим результатом. Создавайте новую страницу только при отсутствии приемлемого кандидата и важности статьи.
4. Для каждой записываемой или редактируемой сущности запишите обратную ссылку в том же ходу.
5. Создавайте `wiki/people/{slug}.md` только для статей с importance ≥ 4.
6. При создании `wiki/concepts/{slug}.md` и принадлежности концепции к теме установите `parent_topic: <topic-slug>`.

### Шаг 5: Рёбра между статьями и `cited_by`

Пропустите весь этот шаг в РЕЖИМЕ INIT — родительский `/init` обрабатывает его при слиянии.

```bash
"$PYTHON_BIN" tools/fetch_s2.py references <arxiv-id>
"$PYTHON_BIN" tools/fetch_s2.py citations <arxiv-id>
```

### Шаг 6: Темы и индекс

1. Сопоставьте теги статьи с существующими `wiki/topics/*.md`. Для каждого совпадения:
   - importance ≥ 4 → добавьте в `## Seminal works` темы И добавьте `[[paper-slug]]` в `key_papers`
   - importance < 4 → добавьте в `## SOTA tracker` или `## Recent work` по году
2. Не создавайте новые страницы тем из `/ingest` — создание тем принадлежит `/init` и `/edit`.
3. Добавьте новые или отредактированные записи страниц в `wiki/index.md`.

### Шаг 7: Журнал и пересборка

```bash
"$PYTHON_BIN" tools/research_wiki.py log wiki/ "ingest | добавлено papers/<slug> | обновлено: <список>"
```

Если не в РЕЖИМЕ INIT:
```bash
"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/
"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/
```

### Шаг 7.5: Опциональная визуализация (только при --visualize)

Пропустите этот шаг, если пользователь явно не передал `--visualize`. Также пропустите в РЕЖИМЕ INIT.

### Шаг 8: Отчёт

Выведите одну компактную сводку, покрывающую: созданные страницы, обновлённые страницы, добавленные графовые рёбра, обнаруженные противоречия (если есть) и высокопороговые ссылки, ещё не существующие в wiki.

### Шаг 9: Опциональное обнаружение (только при --discover)

Пропустите этот шаг, если пользователь явно не передал `--discover`.

## Ограничения

- `raw/papers/`, `raw/notes/`, `raw/web/` принадлежат пользователю и доступны только для чтения.
- `wiki/graph/` принадлежит инструментам. Редактируйте только через `tools/research_wiki.py`.
- Slug'и всегда поступают из `tools/research_wiki.py slug`. Никогда не создавайте вручную.
- Каждая прямая ссылка записывает свою обратную ссылку в том же ходу — инвариант двунаправленных ссылок wiki.
- `/ingest` выполняет проверку формы своего собственного вывода и останавливается на этом.
- Предполагайте, что другой `/ingest` может выполняться конкурентно в sibling worktree.

## Обработка ошибок

См. `references/error-handling.md`. Ключевые моменты: ошибки парсинга источника каскадируют tex → PDF → vision API → ручная передача; простои S2 устанавливают `importance` по умолчанию 3 и пропускают обратное заполнение цитат; простои DeepXiv молча пропускают обогащение; коллизии slug'ов добавляют численный суффикс.

## Зависимости

### Инструменты (через Bash)
- `"$PYTHON_BIN" tools/research_wiki.py slug "<title>"`
- `"$PYTHON_BIN" tools/research_wiki.py find-similar-concept wiki/ "<title>" --aliases "<a,b,c>"`
- `"$PYTHON_BIN" tools/research_wiki.py add-edge wiki/ --from <id> --to <id> --type <type> --evidence "<text>" [--confidence high|medium|low]`
- `"$PYTHON_BIN" tools/research_wiki.py add-citation wiki/ --from papers/<citing> --to papers/<cited> --source semantic_scholar`
- `"$PYTHON_BIN" tools/research_wiki.py log wiki/ "<message>"`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-context-brief wiki/`
- `"$PYTHON_BIN" tools/research_wiki.py rebuild-open-questions wiki/`
- `"$PYTHON_BIN" tools/prepare_paper_source.py --raw-root raw --source <local-path> [--title "<recovered-title>"] [--arxiv-id "<recovered-arxiv-id>"]`
- `"$PYTHON_BIN" tools/init_discovery.py download --raw-root raw --arxiv-id <id> --title "<title-or-id>"`
- `"$PYTHON_BIN" tools/fetch_s2.py paper|citations|references <arxiv-id>`
- `"$PYTHON_BIN" tools/fetch_deepxiv.py brief|head|social <arxiv-id>`
- `"$PYTHON_BIN" tools/discover.py from-anchors --id <arxiv-id> --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown`
- `"$PYTHON_BIN" tools/visualize.py generate-canvas wiki/`

### Общие справочники
- `.claude/skills/shared-references/citation-verification.md`

### Навыки
- `/init` — вызывает `/ingest` в параллельных подагентах через РЕЖИМ INIT
- `/check` — проверяет состояние wiki после завершения `/ingest`
- `/discover` — опциональное продолжение при --discover
- `/visualize` — Шаг 7.5 при --visualize и не в РЕЖИМЕ INIT

### Внешние API
- Semantic Scholar (через `tools/fetch_s2.py`)
- DeepXiv (через `tools/fetch_deepxiv.py`, опционально)
- arXiv (загрузка источников)
