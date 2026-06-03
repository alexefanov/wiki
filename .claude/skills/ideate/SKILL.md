---
name: ideate
description: Многоэтапный пайплайн генерации исследовательских идей — обзор ландшафта → двухмодельный мозговой штурм → фильтрация и валидация → запись в wiki → пилот
argument-hint: "[research-direction-or-topic] [--max-ideas N] [--skip-validation] [--skip-pilot] [--auto]"
---

# /ideate

> Генерация высококачественных исследовательских идей через 5-этапный пайплайн, основанный на базе знаний wiki и внешнем поиске.
> Этап 1 сканирует ландшафт исследований (wiki + WebSearch + S2), Этап 2 запускает двухмодельный мозговой штурм (Claude + Review LLM независимо),
> Этап 3 применяет первичную фильтрацию + глубокую валидацию (осуществимость, новизна, проверка), Этап 4 записывает идеи в wiki (включая отсеянные идеи с причинами провала),
> Этап 5 запускает пилотные эксперименты для выживших идей и обновляет результаты.

## Входы

- `direction` (опционально): направление исследований, ключевые слова или конкретное описание проблемы
- `--max-ideas N` (опционально, по умолчанию 3): максимальное количество идей для записи в wiki
- `--skip-validation`: пропуск Этапа 3 Шага 2 глубокой валидации
- `--skip-pilot`: пропуск пилотных экспериментов Этапа 5
- `--auto`: полностью автоматический режим

## Выходы

- `wiki/ideas/{slug}.md` — по одной странице на идею (статус: proposed)
- `wiki/graph/edges.jsonl` — новые рёбра idea → concept/topic
- `wiki/graph/context_brief.md` — пересобранный сжатый контекст
- `wiki/graph/open_questions.md` — пересобранная карта пробелов
- **IDEA_REPORT** (выводится в терминал)

## Взаимодействие с Wiki

### Чтение
- `wiki/graph/context_brief.md`, `wiki/graph/open_questions.md`
- `wiki/ideas/*.md`, `wiki/papers/*.md`, `wiki/concepts/*.md`, `wiki/methods/*.md`, `wiki/topics/*.md`, `wiki/experiments/*.md`

### Запись
- `wiki/ideas/{slug}.md` — создание новых страниц идей
- `wiki/graph/edges.jsonl` — добавление рёбер addresses_gap, inspired_by
- `wiki/graph/context_brief.md`, `wiki/graph/open_questions.md` — пересборка
- `wiki/log.md` — добавление в журнал

### Создаваемые графовые рёбра
- `addresses_gap`: idea → concept/topic
- `inspired_by`: idea → paper/method/concept

## Рабочий процесс

**Предусловия**:
1. Убедитесь, что рабочая директория — корень проекта wiki
2. **Проверка зрелости wiki**: `python3 tools/research_wiki.py maturity wiki/ --json`
   - cold: расширение внешнего поиска
   - warm: стандартное поведение
   - hot: сужение внешнего поиска, повышение gap_alignment_bonus
3. **Снимок состояния wiki** для отчёта о росте

### Этап 1: Обзор ландшафта

Цель: построение всеобъемлющего представления о целевом домене.

1. **Загрузка внутреннего контекста wiki**
2. **Внешний поиск** (параллельно через инструмент Agent):
   - WebSearch, Semantic Scholar, DeepXiv, arXiv
3. **Составление отчёта о ландшафте** (для внутреннего использования)

### Этап 2: Двумодельный мозговой штурм

**Следуйте shared-references/cross-model-review.md**

1. **Claude генерирует 6–10 идей** по 5 структурированным путям (A-E)
2. **Review LLM независимо генерирует 4–6 идей**
3. **Объединение и дедупликация**: 8–12 кандидатов

### Этап 3: Фильтрация и валидация

**Шаг 1 — Первичная фильтрация**: проверка осуществимости, быстрая проверка новизны, соответствие wiki
**Шаг 2 — Глубокая валидация** (если не --skip-validation): /novelty + /review

### Этап 4: Запись в wiki

1. **Запись топ-идей** (статус: proposed) с полным frontmatter и телом
2. **Запись отсеянных идей** (статус: failed) с failure_reason
3. **Добавление графовых рёбер**
4. **Пересборка производных данных**
5. **Добавление в журнал**
6. **Вывод IDEA_REPORT**

### Этап 5: Пилотные эксперименты

(Пропуск при --skip-pilot)

Выполнение пилотных экспериментов для выбранных пользователем выживших идей через:
1. Создание спецификации пилота (YAML)
2. Запуск через `/exp-pilot-run`
3. Оценка через `/exp-pilot-eval`

## Ограничения

- **Авто-переключение в cold-start mode** при пустой wiki
- **Каждая идея должна иметь привязку к wiki**
- **Черный список обязателен**
- **Независимость Review LLM**
- **Отсеянные идеи также записываются в wiki**
- **Без фабрикаций**
- **Уникальность slug'ов**
- **Графовые рёбра через tools/research_wiki.py**

## Обработка ошибок

- **Wiki пуста**: продолжите с внешним поиском
- **WebSearch/ Semantic Scholar/DeepXiv недоступны**: градация до доступных источников
- **Review LLM недоступен**: использование только Claude
- **/novelty или /review завершились ошибкой**: пометка и продолжение
- **Пилот завершился ошибкой**: пометка с [pilot] в failure_reason
- **Все пилоты завершились ошибкой**: отчёт с рекомендациями
- **Конфликт slug'ов**: добавление численного суффикса

## Зависимости

### Инструменты (через Bash)
- `python3 tools/research_wiki.py maturity wiki/ --json`
- `python3 tools/research_wiki.py slug "<title>"`
- `python3 tools/research_wiki.py add-edge wiki/ ...`
- `python3 tools/research_wiki.py rebuild-context-brief wiki/`
- `python3 tools/research_wiki.py rebuild-open-questions wiki/`
- `python3 tools/research_wiki.py log wiki/ "<message>"`
- `python3 tools/fetch_s2.py search "<query>" --limit 20`
- `python3 tools/fetch_deepxiv.py search "<query>" --mode hybrid --limit 20`
- `python3 tools/fetch_deepxiv.py brief <arxiv_id>`
- `python3 tools/fetch_deepxiv.py trending --days 14`

### Навыки (через инструмент Skill)
- `/novelty`, `/review`, `/exp-pilot-run`, `/exp-pilot-eval`

### MCP-серверы
- `mcp__llm-review__chat` — Этап 2 Review LLM

### Claude Code Native
- `WebSearch`, `Agent` tool

### Общие справочники
- `.claude/skills/shared-references/cross-model-review.md`
