---
name: prefill
description: Заполнение wiki/foundations/ фоновыми знаниями домена, чтобы последующий /ingest не создавал дублирующие страницы концепций для учебного материала
argument-hint: "[domain] [--add 'concept name']"
---

# /prefill

> Осаждает фундаментальный фон (ключевые методы, общепринятые практики, стандартные архитектуры) в `wiki/foundations/` как **терминальные** страницы.
> Foundations по дизайну однонаправленные: другие страницы ссылаются на них, foundations не записывают обратных ссылок.

## Триггер

Ручной запуск: `/prefill [domain]` или `/prefill --add "concept name"`.

## Входы

- `domain` *(позиционный, опционально)*: исследовательский домен — один из `general`, `NLP`, `CV`, `ML Systems`, `Robotics`. Если не указан, определите по тегам `wiki/topics/`; если `wiki/topics/` пуст, спросите пользователя.
- `--add "<concept>"`: пропустите каталог и заполните ровно одну foundation по имени.

## Выходы

- `wiki/foundations/{slug}.md` — по одной странице на заполненную концепцию
- Обновлённый `wiki/index.md` (раздел foundations пересобирается через `rebuild-index`)
- Запись `wiki/log.md`

## Взаимодействие с Wiki

### Чтение
- `wiki/topics/*.md` — для определения домена (когда `domain` не указан)
- `wiki/foundations/*.md` — для пропуска уже заполненных концепций (идемпотентно)
- `.claude/skills/prefill/foundations-catalog.yaml` — список заполнения

### Запись
- `wiki/foundations/{slug}.md` (только новые — никогда не перезаписывать)
- `wiki/index.md` (через `tools/research_wiki.py rebuild-index`)
- `wiki/log.md` (через `tools/research_wiki.py log`)

## Рабочий процесс

**Предусловия**: рабочая директория содержит `wiki/`, `tools/`, `.claude/`. Установите `WIKI_ROOT=wiki/`.

### Шаг 1: Определение домена

1. Если аргумент `domain` задан → используйте его.
2. Иначе если режим `--add` → домен `general`, если пользователь не указал иной.
3. Иначе: прочитайте все `wiki/topics/*.md` frontmatter `tags`; если обнаружен единый доминирующий домен, используйте его; иначе спросите пользователя.

### Шаг 2: Загрузка набора данных

- **Режим каталога**: прочитайте `.claude/skills/prefill/foundations-catalog.yaml`. Выберите все записи в `domains.{domain}` плюс всё в `domains.general` (общие foundations применяются ко всем областям исследований).
- **Режим `--add`**: синтезируйте одну запись `{slug: <slugified concept>, title: <concept>, summary: ""}`. Используйте `python3 tools/research_wiki.py slug "<concept>"` для получения slug.

Для каждой записи проверьте `wiki/foundations/{slug}.md`. Если уже существует, **пропустите** (не перезаписывайте, не предупреждайте).

### Шаг 3: Получение фона из Wikipedia

Для каждой оставшейся записи вызовите `tools/fetch_wikipedia.py`:

```bash
python3 tools/fetch_wikipedia.py summary "<title>"
python3 tools/fetch_wikipedia.py sections "<title>"
python3 tools/fetch_wikipedia.py section "<title>" --index <N>   # для релевантных разделов
```

- Вызов summary возвращает `{title, extract, url}`.
- Вызов sections возвращает список `{index, line, level}` — выберите разделы, чей `line` совпадает с `Variants`, `Types`, `Architecture`, `History`, `Limitations`, `Applications` (поиск подстроки без учёта регистра).
- Код выхода `2` из любого вызова означает **страница не найдена** — переход к знаниям LLM для этой записи и установка `source_url: ""` в результирующем frontmatter.

### Шаг 4: Составление страницы foundation

Сформируйте каждую запись в шаблоне ниже. Различайте контекст, полученный из Wikipedia, от контекста, предоставленного LLM, добавляя `(LLM analysis)` к разделам без материала-источника из Wikipedia.

```yaml
---
title: "{title}"
slug: "{slug}"
domain: "{domain}"
status: mainstream         # или historical, если запись — устаревшая техника
aliases: []                # перечислите любые распространённые aliases, в которых LLM уверен
first_introduced: "{год, если есть в сводке Wikipedia, иначе пусто}"
date_updated: "{сегодня}"
source_url: "{url wikipedia, или пусто при 404}"
---

## Определение
Первый абзац сводки Wikipedia или определение, предоставленное LLM.

## Интуиция
Понятное объяснение, построенное на определении.

## Формальные обозначения
Математика/обозначения, извлечённые из Wikipedia, или предоставленные LLM с пометкой `(LLM analysis)`.

## Ключевые варианты
Маркированный список, полученный из разделов Wikipedia "Variants"/"Types"/"Architecture".

## Известные ограничения
Из Wikipedia + суждение LLM.

## Открытые проблемы
Анализ LLM (LLM analysis)

## Релевантность для активных исследований
Анализ LLM (LLM analysis)
```

Запишите каждый файл в `wiki/foundations/{slug}.md`.

### Шаг 5: Обновление навигации и журнала

```bash
python3 tools/research_wiki.py rebuild-index wiki/
python3 tools/research_wiki.py log wiki/ "prefill | создано {N} foundations для {domain}"
```

### Шаг 6: Отчёт

Выведите сгруппированную сводку:

```
## Отчёт prefill — {дата}

**Домен**: {domain}
**Создано**: {N}  **Пропущено (уже есть)**: {M}

### mainstream
- foundations/gradient-descent — Gradient Descent
- ...

### historical
- foundations/recurrent-neural-networks — Recurrent Neural Networks
```

Напомните пользователю, что последующие запуски `/ingest` будут дедуплицировать по этим foundations и создавать wikilinks (`[[foundation-slug]]`) вместо новых страниц концепций.

## Ограничения

- **foundations терминальны**: никогда не записывайте `key_papers`, `related_concepts` или какие-либо исходящие ссылочные поля на странице foundation. Другие страницы могут ссылаться на них.
- **никогда не перезаписывайте** существующий `wiki/foundations/{slug}.md` (идемпотентные повторные запуски)
- **различайте источники**: контекст из Wikipedia должен быть визуально отделён от контекста, предоставленного LLM, в теле страницы
- **каталог является рекомендательным**: YAML-список заполнения редактируется вручную и неполон. Пользователи могут расширять его без изменений кода
- **записывает только в `wiki/foundations/`**: никогда не создавайте страницы в `papers/`, `concepts/`, `topics/` и т.д.

## Обработка ошибок

- **`wiki/foundations/` не существует**: сначала запустите `python3 tools/research_wiki.py init wiki/`.
- **Wikipedia 404**: запишите отсутствующую страницу, перейдите к знаниям LLM для этой записи (`source_url: ""`).
- **Ошибка сети**: выведите, какие записи не удалось загрузить, и продолжите с остальными; не прерывайте весь пакет.
- **Файл каталога отсутствует**: выведите ошибку, указывающую на `.claude/skills/prefill/foundations-catalog.yaml`.

## Зависимости

### Инструменты (через Bash)
- `python3 tools/fetch_wikipedia.py summary|sections|section|wikitext "<title>" [--index N]`
- `python3 tools/research_wiki.py slug "<title>"`
- `python3 tools/research_wiki.py rebuild-index wiki/`
- `python3 tools/research_wiki.py log wiki/ "<message>"`

### Каталог
- `.claude/skills/prefill/foundations-catalog.yaml`
