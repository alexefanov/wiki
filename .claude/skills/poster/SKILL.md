---
name: poster
description: Генерация академического постера из написанной статьи — дистилляция разделов в одностраничный HTML-постер с фигурами и переходами между разделами
argument-hint: "[paper-dir] [--review] [--anonymous] [--no-figures] [--no-logos] [--no-refine]"
---

# /poster

> Генерация академического HTML-постера из написанной статьи. Чтение `paper/main.tex`,
> файлов разделов и фигур; построение промежуточного `dag.json`, совместимого с PaperX;
> дистилляция каждого раздела в 2–5-предложенийное резюме; выбор репрезентативных фигур;
> рендеринг в автономный HTML-постер с 3-колоночным авто-подгоняющимся макетом.

## Входы

### Общие

- `paper_dir` (опционально, по умолчанию `paper/`): директория проекта LaTeX с `main.tex` и `sections/`
- `--review` (опционально): кросс-модельная проверка Review LLM сгенерированного содержимого постера
- `--anonymous` (опционально): принудительно "Anonymous" независимо от `\author{}`
- `--no-figures` (опционально): рендер каждого раздела только текстом
- `--no-logos` (опционально): пропуск подсказок логотипов учреждений/конференций
- `--no-refine` (опционально): пропуск критико-правочного шага 5.5

### Силовые пользователи (скриптовое использование)

- `--authors STR`: переопределение текста авторов на постере
- `--venue STR`: текст площадки для правого верхнего блока
- `--affiliation-logo PATH` / `--conference-logo PATH`: пути к файлам логотипов
- `--layout corners|stacked` (по умолчанию `corners`): макет заголовка
- `--auto-figures`: пропуск вопросов о фигурах по разделам
- `--refine-iterations N` (по умолчанию 1, макс. 2): количество проходов критико-правки

## Выходы

- `poster/dag.json` — промежуточный формат PaperX (переиспользуемый будущими `/slides`, `/pr`)
- `poster/outline.html` — объединённые блоки `<section>` до инъекции шаблона
- `poster/poster.html` — финальный автономный HTML-постер
- `poster/poster.png` — скриншот рендеринга при 2× CSS размерах
- `poster/images/` — сконвертированные фигуры (PDF→PNG @ 200 DPI)
- **POSTER_REPORT** (выводится в терминал)
- `wiki/log.md` — добавлена запись в журнал

## Взаимодействие с Wiki

### Чтение
- `paper/main.tex` + `paper/sections/*.tex` + `paper/figures/` — исходники статьи
- `wiki/outputs/paper-plan-*.md` (опционально) — повествовательная弧, план фигур
- `wiki/ideas/*.md` (опционально) — гипотеза, аргумент о новизне
- `wiki/experiments/*.md` (опционально) — ключевые результаты
- `.claude/skills/shared-references/academic-writing.md` — правила удаления AI-маркеров

### Запись
- Директория `poster/` (все файлы из раздела Выходы)
- `wiki/log.md` — добавлена запись

### Создаваемые графовые рёбра
- Нет (постер — артефакт презентации, а не сущность знаний)

## Рабочий процесс

**Предусловие**: убедитесь, что `paper/main.tex` существует. Если нет — ошибка "Сначала запустите /paper-draft."

### Шаг 0: Интерактивная конфигурация заголовка

Цель: сбор текста площадки и (опционально) двух логотипов для рендеринга в заголовке постера.

Авторы разрешаются с приоритетом:
1. Флаг `--authors STR`
2. Флаг `--anonymous`
3. Кэш `paper/.author_display.txt`
4. Содержимое dag.json из `\author{...}`
5. **Иначе**: СПРОСИТЬ пользователя

Текст площадки запрашивается, если `--venue` не передан.

Логотипы запрашиваются через `AskUserQuestion`, если не переданы соответствующие флаги.

### Шаг 1: Построение dag.json

```bash
python3 tools/wiki2dag.py build --paper-dir paper/ --output poster/dag.json [--anonymous]
```

### Шаг 2: Сборка WIKI_CONTEXT (опционально)

Опциональное использование плана статьи для обогащения промптов дистилляции.

### Шаг 2.5: Выбор фигур

Определение, какие фигуры (если есть) принадлежат каждому выбранному разделу.

### Шаг 3: Дистилляция разделов постера

Загрузка `poster/dag.json` и словаря решений о фигурах. Итерация по выбранным узлам разделов.

### Шаг 4: Добавление переходов между разделами

Генерация связующих предложений для плавного перехода между разделами.

### Шаг 5: Построение постера

```bash
python3 tools/poster.py build --template templates/poster/poster_template.html --outline poster/outline.html --output poster/poster.html
python3 tools/poster.py inject-title --dag poster/dag.json [--authors "..."] poster/poster.html
python3 tools/poster.py inject-header --venue "..." [--affiliation-logo {path}] [--conference-logo {path}] --layout {corners|stacked} poster/poster.html
python3 tools/poster.py inject-figures --dag poster/dag.json --paper-dir paper/ --poster-dir poster/
python3 tools/poster.py validate poster/poster.html
```

### Шаг 5b: Рендер PNG

```bash
python3 tools/poster.py render poster/poster.html
```

### Шаг 5.5: Критико-правка через Claude (скриншот + отчёт о переполнении DOM)

Автоматическое применение; без взаимодействия с пользователем.

### Шаг 6: Опциональная проверка Review LLM (--review)

### Шаг 7: Журнал и отчёт

## Ограничения

- Не изменяйте файлы-исходники `paper/`
- Не создавайте сущности wiki или графовые рёбра
- Переиспользуйте скомпилированные фигуры
- Уважайте `--anonymous`
- Максимум 6 разделов
- Резюме не более 40 слов
- Удаление AI-маркеров обязательно
- Строгое遵循 шаблона инъекции

## Обработка ошибок

- `paper/main.tex` не найден
- Нет фигур
- `pdftoppm` не установлен
- Нет поддерживаемого браузера для `render`
- Ошибка валидации

## Зависимости

### Инструменты (через Bash)
- `python3 tools/wiki2dag.py build ...`
- `python3 tools/poster.py build|inject-title|inject-header|inject-figures|validate|render|check-overflow ...`
- `python3 tools/research_wiki.py log wiki/ "<message>"`
- `pdflatex` (для растеризации TikZ)
- `pdftoppm` (PDF → PNG)
- Playwright + Chromium (предпочтительно)

### MCP-серверы
- `mcp__llm-review__chat` — опциональная кросс-модельная проверка

### Claude Code Native
- `Read`, `Write`, `Edit`, `Bash`

### Общие справочники
- `.claude/skills/shared-references/academic-writing.md`
- `.claude/skills/shared-references/cross-model-review.md`

### Вызывается из
- Ручной вызов пользователя
