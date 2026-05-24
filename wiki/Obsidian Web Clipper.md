---
type: концепция
title: Obsidian Web Clipper
domain: llm_wiki
description: "Web Clipper удобен как вход в raw/: он позволяет быстро сохранять статьи и web-страницы в markdown, после чего LLM может выполнить LLM Wiki Workflow и обновить wiki/. Clip web pages - сохранение страниц."
tags:
  - llm_wiki
  - obsidian
  - workflow
  - концепция
raw_source: "raw/`:"
---

# Obsidian Web Clipper

Obsidian Web Clipper - browser extension для сохранения web-страниц, highlights и выбранного контента в Obsidian vault.

## Роль в этом vault

Web Clipper удобен как вход в `raw/`: он позволяет быстро сохранять статьи и web-страницы в markdown, после чего LLM может выполнить [[LLM Wiki Workflow|ingest]] и обновить `wiki/`.

## Возможности

- Clip web pages - сохранение страниц.
- Highlighter - выделение важных фрагментов.
- Reader - чтение страницы в очищенном виде.
- Interpreter - prompt-based обработка данных на странице.
- Templates, variables, filters, logic - настройка формата сохранения.

## Privacy

Официальный источник утверждает, что Web Clipper сохраняет контент локально в vault, не собирает usage metrics и имеет open-source код.

## Практическая связка

1. Сохранить источник через Web Clipper в `raw/`.
2. Попросить LLM ingest-ить конкретный файл.
3. Проверить обновленные страницы в [[index]].
4. При необходимости запустить lint.

## Источники

- [raw/llm/Introduction to Obsidian Web Clipper.md](../raw/llm/Introduction%20to%20Obsidian%20Web%20Clipper.md)
- [raw/llm/llm-wiki.md](../raw/llm/llm-wiki.md)
- [raw/Building my Personal LLM Wiki (Part 1) The Motivation.md](<Building my Personal LLM Wiki (Part 1) The Motivation.md>)

## Связи

- [[Obsidian]]
- [[LLM Wiki Workflow]]
- [[Source Notes]]

## Развитие

- Какие источники нужны для углубления.
- Какие подстраницы можно создать.
