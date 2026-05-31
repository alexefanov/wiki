---
description: 'Визуализация [--obsidian] [--canvas] [--focus NODE] [--depth N] [--types TYPE,...] [--edge-types TYPE,...] [--all]'
---

Обнови визуализацию графа знаний, используя скилл `visualize`.

Аргументы: $ARGUMENTS

## Флаги

- `--obsidian` — обновить Obsidian-связи в wiki/ (tools/research_wiki.py --wiki-links)
- `--canvas` — сгенерировать .canvas файл для Obsidian
- `--focus <node_id>` — визуализировать окрестность указанного узла
- `--depth N` — глубина визуализации (по умолчанию 2)
- `--types <type,...>` — фильтр по типам страниц через запятую (papers, ideas, methods и т.д.)
- `--edge-types <type,...>` — фильтр по типам рёбер через запятую
- `--all` — показать все узлы и связи (без фильтров)

## Примеры

```
/visualize
/visualize --obsidian
/visualize --canvas
/visualize --focus idea-2024-001 --depth 3
/visualize --types papers,ideas --edge-types цитирует,использует
/visualize --all
```

Порядок действий:
1. Определи флаги из аргументов
2. Если флагов нет — обнови стандартную визуализацию
3. Вызови скилл `visualize` с флагами
