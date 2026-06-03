# Дисциплина цитирования

> Общий справочник для всех навыков, генерирующих цитаты: /paper-draft, /survey, /paper-plan.
> Каждая цитата в выводе OmegaWiki должна быть **верифицируемой** — никогда не генерированной LLM.

---

## Основное правило

**Записи BibTeX должны поступать из авторитетных источников, а не из памяти LLM.**

LLM галлюцинируют детали цитат (неправильный год, неправильная площадка, неправильные авторы, несуществующие статьи).
Единственные допустимые источники для BibTeX:

1. **DBLP** (`https://dblp.org/`) — основной источник для площадок CS
2. **CrossRef** (`https://api.crossref.org/`) — основной источник для публикаций с DOI
3. **Semantic Scholar** (`https://api.semanticscholar.org/`) — запасной для препринтов
4. **Собственный .bib файл статьи** — если доступен в `raw/papers/`

## Протокол [UNCONFIRMED]

Когда запись BibTeX **не может** быть получена ни из одного авторитетного источника:

1. Сгенерируйте запись из доступной информации (заголовок, авторы, год из wiki-страницы)
2. Добавьте префикс `UNCONFIRMED_` к ключу BibTeX: `@article{UNCONFIRMED_smith2024attention, ...}`
3. Добавьте комментарий: `% [UNCONFIRMED] BibTeX not confirmed from DBLP/CrossRef — manual check required`
4. Маркер `[UNCONFIRMED]` является **жёстким блокатором** подачи — /paper-compile должен пометить все оставшиеся записи `[UNCONFIRMED]`

## Извлечение BibTeX

### DBLP (предпочтительно для CS)

```bash
# Поиск по заголовку
WebFetch: https://dblp.org/search/publ/api?q={url-encoded-title}&format=json&h=3

# Парсинг ответа: .result.hits.hit[].info содержит title, authors, venue, year, url
# Получение BibTeX: WebFetch по полю .url + суффикс ".bib"
```

### CrossRef (предпочтительно для DOI)

```bash
# Поиск по заголовку
WebFetch: https://api.crossref.org/works?query.bibliographic={url-encoded-title}&rows=3

# Парсинг ответа: .message.items[] содержит title, author, container-title, DOI
# Построение BibTeX из структурированных данных
```

### Semantic Scholar (засной для препринтов arXiv)

```bash
# Используйте tools/fetch_s2.py, который уже есть в проекте
python3 tools/fetch_s2.py search "<title>"
# Возвращает paperId, title, authors, year, venue, externalIds
```

## Конвенция ключей цитат

```
{фамилия-первого-автора}{год}{первое-ключевое-слово}
```

Примеры:
- `hu2022lora` (Hu et al., 2022, "LoRA: Low-Rank Adaptation...")
- `vaswani2017attention` (Vaswani et al., 2017, "Attention Is All You Need")

## Правила для навыков

### /paper-draft
1. После написания каждого раздела соберите все ссылки `\cite{}`
2. Для каждой цитаты: попробуйте DBLP → CrossRef → S2 по порядку
3. Включайте только записи, которые фактически цитируются (`\nocite{*}` запрещён)
4. Запишите `references.bib` с полученными записями + записи [UNCONFIRMED] отдельно внизу

### /survey
1. Используйте wikilinks `[[slug]]` при написании (внутренний формат wiki)
2. При преобразовании в LaTeX разрешите каждый `[[slug]]` в `\cite{key}`
3. Ключ цитаты должен соответствовать верифицированной записи BibTeX
4. Если у wiki-статьи нет верифицируемого BibTeX, выведите `\cite{UNCONFIRMED_slug}` и пометьте

### /paper-plan
1. В плане цитат перечислите все wiki-статьи, которые будут цитироваться
2. Предварительно извлекайте BibTeX для каждой запланированной цитаты (быстрое обнаружение: выявите записи [UNCONFIRMED] заранее)
3. Сообщите покрытие цитат: сколько верифицировано vs [UNCONFIRMED]

## Чего НЕ ДЕЛАТЬ

- **Никогда** не генерируйте BibTeX из памяти (неправильная площадка/год хуже, чем [UNCONFIRMED])
- **Никогда** не цитируйте статью, отсутствующую в wiki (все цитаты восходят к wiki/papers/)
- **Никогда** не используйте `\nocite{*}` (каждая запись должна быть явно указана)
- **Никогда** не удаляйте молча маркер [UNCONFIRMED] (он должен сохраняться до ручной проверки или успешного извлечения)
- **Никогда** не фабрикуйте DOI или ID arXiv
