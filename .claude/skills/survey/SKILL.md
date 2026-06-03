---
name: survey
description: Генерация раздела Related Work для статьи из знаний wiki — тематическая группировка → структура повествования → вывод LaTeX, следуя citation-verification и academic-writing
argument-hint: <research-question-or-idea-slugs> [--format latex|markdown] [--max-papers 30]
---

# /survey

> Генерация раздела Related Work, готового к прямому использованию в статье, на основе существующих знаний wiki.
> Материал берётся из wiki/papers/, concepts/, topics/; группировка по направлению (не листинг статей).
> Каждая группа завершается утверждением о том, чем она отличается от этой работы. Цитаты следуют citation-verification.md;
> написание следует правилам Related Work из academic-writing.md.
> Поддерживает форматы вывода LaTeX и Markdown.

## Входы

- `query`: одно из:
  - описание исследовательского вопроса (свободный текст, например, "parameter-efficient fine-tuning for LLMs")
  - список slug'ов идей (из wiki/ideas/, используется для организации связанной работы вокруг конкретных идей)
  - путь к PAPER_PLAN.md (извлечение определения раздела Related Work)
- `--format` (опционально, по умолчанию `latex`): формат вывода
  - `latex`: цитаты `\cite{key}`, встраиваемые непосредственно в статью
  - `markdown`: цитаты wikilink `[[slug]]`, для архивации в wiki
- `--max-papers` (опционально, по умолчанию 30): максимальное количество цитируемых статей

## Выходы

- `wiki/outputs/related-work-{slug}-{date}.md` — текст Related Work (архивный)
- `wiki/graph/edges.jsonl` — рёбра derived_from (если создан новый вывод)
- `wiki/log.md` — добавлена запись в журнал
- **Вывод в терминал** — текст тела Related Work (для прямого копирования)

## Взаимодействие с Wiki

### Чтение
- `wiki/papers/*.md` — Problem & Context, Key idea, Experiment & Results, Related, My take
- `wiki/concepts/*.md` — Definition, Variants, Comparison, Known limitations
- `wiki/topics/*.md` — Overview, Timeline, Open problems, Seminal works
- `wiki/ideas/*.md` — Hypothesis, Motivation, origin_gaps (если вход — slug'и идей)
- `wiki/methods/*.md` — Mechanism, Procedure, source_papers (когда идеи ссылаются на методы)
- `wiki/index.md` — каталог содержимого, фильтрованный по важности
- `wiki/graph/context_brief.md` — глобальный контекст
- `wiki/graph/edges.jsonl` — межстатьевые семантические отношения (same_problem_as, similar_method_to, builds_on, challenges)
- `.claude/skills/shared-references/academic-writing.md` — правила написания Related Work
- `.claude/skills/shared-references/citation-verification.md` — дисциплина цитирования

### Запись
- `wiki/outputs/related-work-{slug}-{date}.md` — архивный файл
- `wiki/graph/edges.jsonl` — рёбра derived_from
- `wiki/log.md` — добавлена запись в журнал операций

### Создаваемые графовые рёбра
- `derived_from`: вывод related-work → исходные статьи

## Рабочий процесс

**Предусловие**: убедитесь, что рабочая директория — корень проекта wiki (директория, содержащая `wiki/`, `raw/`, `tools/`).

### Шаг 1: Поиск релевантных знаний

1. **Парсинг входа**:
   - Если свободный текст: извлеките ключевые слова; сопоставьте с тегами и заголовками в wiki/index.md
   - Если slug'и идей: прочитайте `origin_gaps` каждой идеи (концепции/темы) и пройдите к `concepts.key_papers` и базовым работам тем для сбора связанных статей; также прочитайте методы, связанные из `## Approach sketch` идеи, и извлеките их `source_papers`
   - Если путь к PAPER_PLAN: прочитайте группировки и цитаты раздела Related Work
2. Прочитайте `wiki/graph/context_brief.md` для глобального контекста
3. Прочитайте `wiki/graph/edges.jsonl`: извлеките межстатьевые семантические отношения (same_problem_as, similar_method_to, builds_on, challenges)
4. **Построение списка кандидатов статей**:
   - Сортировка по убыванию важности из index.md
   - Ранжирование по совпадению тегов и домена
   - Ограничение `--max-papers` статей
5. **Если кандидатов < 5**: предупредите "недостаточно связанных статей; рассмотрите /ingest большего количества статей"

### Шаг 2: Глубокое чтение связанных страниц

Для каждой статьи в списке кандидатов:

1. Прочитайте `wiki/papers/{slug}.md`: фокус на Problem & Context, Key idea, Experiment & Results, My take
2. Прочитайте связанные `wiki/concepts/*.md`: фокус на Definition, Variants, Comparison
3. Прочитайте связанные `wiki/topics/*.md`: фокус на Timeline, Open problems

Запишите для каждой статьи:
- основной вклад (одно предложение)
- категория метода (к какому направлению исследований относится)
- отношение к этой работе (та же проблема / похожий метод / основана на / оспаривает)
- ограничения (извлечённые из Limitations или My take)

### Шаг 3: Тематическая группировка

Следуя правилам Related Work в `shared-references/academic-writing.md`:

1. **Группировка по направлению** (не листинг статей):
   - Извлечение естественных группировок из классификаций wiki/topics/ и concepts/
   - 3–8 статей на группу
   - Заголовки групп описывают направления исследований (например, "Parameter-Efficient Fine-Tuning"), а не отдельные статьи
2. **Определение порядка групп**:
   - От широкого к узкому (основное направление → поднаправление → наиболее связанные методы)
   - Или хронологический (базовый → развитие → недавние)
3. **Определение порядка внутри группы**:
   - По возрастанию года (показ прогресса)
   - Важные статьи: 2–3 предложения; второстепенные: 1 предложение
4. **Аннотация отношения группы к этой работе**:
   - Завершите каждую группу одним предложением: "В отличие от этих подходов, наш метод..." или "Мы основываемся на X, ..."

### Шаг 4: Генерация абзацев

Следуя `shared-references/academic-writing.md`:

1. **Один или два абзаца на группу**:
   - Введение: фон и важность направления
   - Тело: расширение вклада каждой статьи в порядке группы
   - Завершение: позиционирование относительно этой работы (обязательно)

2. **Формат цитирования**:
   - `--format latex`: `\cite{key}`, ключ сгенерирован по правилам именования citation-verification.md
   - `--format markdown`: `[[slug]]`

3. **Стандарты написания**:
   - Нет плоских списков ("X сделал Y. Z сделал W.")
   - Каждый абзац имеет предложение-тезис
   - Используйте контрастные связки ("While X focuses on..., Y addresses...")
   - Нет словаря с AI-маркерами (см. список удаления AI в academic-writing.md)

4. **Удаление AI-маркеров**:
   - Сканирование и замена словаря с AI-маркерами
   - Варьирование начал предложений
   - Удаление предложений-заполнителей

### Шаг 5: Подготовка BibTeX (только --format latex)

Если формат вывода — LaTeX, следуя `shared-references/citation-verification.md`:

1. Соберите все цитаты `\cite{key}`
2. Для каждого ключа попробуйте получить BibTeX: DBLP → CrossRef → S2
3. Верифицированные: запишите BibTeX
4. Неверифицированные: пометьте `[UNCONFIRMED]`
5. Выведите список записей BibTeX (можно добавить в paper/references.bib)
6. Сообщите покрытие цитат

### Шаг 6: Архивация

1. **Генерация slug**:
   ```bash
   python3 tools/research_wiki.py slug "<ключевые-слова-запроса>"
   ```

2. **Запись архивного файла**:
   Создайте `wiki/outputs/related-work-{slug}-{date}.md`:
   ```yaml
   ---
   title: "Related Work: {тема}"
   type: related-work
   format: {latex|markdown}
   paper_count: {N}
   date_generated: YYYY-MM-DD
   ---
   ```
   Тело — полный текст Related Work.
   Если формат latex: добавьте записи BibTeX в виде приложения.

3. **Добавление графовых рёбер**:
   ```bash
   # вывод → каждая цитируемая статья
   python3 tools/research_wiki.py add-edge wiki/ \
     --from "outputs/related-work-{slug}-{date}" --to "papers/{paper-slug}" \
     --type derived_from --evidence "Цитировано в разделе related work"
   ```

4. **Добавление в журнал**:
   ```bash
   python3 tools/research_wiki.py log wiki/ \
     "survey | {topic} | {N} статей, {G} групп, формат: {format}"
   ```

5. **Вывод в терминал**: полный текст Related Work + статистика покрытия цитат

## Ограничения

- **Цитируйте только статьи, уже существующие в wiki**: не фабрикуйте цитаты; каждый `\cite{}` или `[[slug]]` должен соответствовать странице в wiki/papers/
- **Группировка по темам, а не плоский список**: каждый абзац покрывает направление, а не "Статья A сделала X. Статья B сделала Y."
- **Каждая группа должна иметь предложение позиционирования**: укажите отношение к этой работе (в конце — отличие или наследование)
- **Предупреждение при кандидатах < 5**: предложите пользователю сначала выполнить /ingest большего количества статей
- **BibTeX следует citation-verification.md**: не генерируйте из памяти LLM (только --format latex)
- **Удаление AI-маркеров обязательно**: проход шлифовки должен быть применён после генерации
- **Архивация в outputs/**: не изменяйте напрямую wiki-страницы papers/concepts/topics
- **Графовые рёбра через tools/research_wiki.py**: не редактируйте вручную edges.jsonl

## Обработка ошибок

- **Менее 3 статей wiki**: ошибка; предложите сначала выполнить /ingest достаточного количества статей
- **Нет подходящих статей**: расширите область поиска (ослабьте сопоставление тегов); если всё ещё нет, ошибка
- **Все извлечения BibTeX не удались** (формат latex): используйте заполнители [UNCONFIRMED]; сообщите количество
- **Несоответствие формата PAPER_PLAN**: игнорируйте предложения по группировке из плана; используйте автоматическую группировку
- **Конфликт slug'ов**: добавьте суффикс даты

## Зависимости

### Инструменты (через Bash)
- `python3 tools/research_wiki.py slug "<title>"` — генерация slug
- `python3 tools/research_wiki.py add-edge wiki/ ...` — добавление графового ребра
- `python3 tools/research_wiki.py log wiki/ "<message>"` — добавление в журнал
- `python3 tools/fetch_s2.py search "<title>"` — резервный BibTeX (поиск S2)

### MCP-серверы
- Нет (survey не требует Review LLM; используйте /review --focus writing для отдельной проверки)

### Claude Code Native
- `Read` — чтение wiki-страниц
- `Glob` — поиск идей, методов, концепций, тем, статей
- `WebFetch` — извлечение BibTeX из DBLP / CrossRef (только --format latex)

### Общие справочники
- `.claude/skills/shared-references/academic-writing.md` — правила написания Related Work + удаление AI-маркеров
- `.claude/skills/shared-references/citation-verification.md` — извлечение BibTeX и протокол [UNCONFIRMED]

### Вызывается из
- `/paper-draft` Шаг 3 (раздел Related Work может быть делегирован этому навыку)
- Ручной вызов пользователя
