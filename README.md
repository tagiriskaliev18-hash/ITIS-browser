# ITIS Browser

> Часть экосистемы **[MindTagSystem](https://github.com/tagiriskaliev18-hash/MindTagSystem)** · автор **Тагир Искалиев** ([@tagiriskaliev18-hash](https://github.com/tagiriskaliev18-hash))

**ITIS — Intelligence Browser** — десктопный браузер со встроенным ИИ-агентом. Агент видит открытую страницу, отвечает на вопросы о ней и сам управляет ею: кликает по ссылкам, кнопкам и видео, прокручивает вверх и вниз.

## Возможности

- **Браузер на Chromium.** Движок QtWebEngine, вкладки, адресная строка, которая понимает и адреса, и поисковые запросы (поиск через Brave Search).
- **Стартовая страница ITIS Search** (`start_page.html`) с фоновыми изображениями и видео.
- **Боковая панель ИИ-агента** в духе HeyClicky. Агент получает адрес и текст страницы, отвечает по-русски и управляет страницей командами:
  - `[CLICK: текст]` — нажать на ссылку, кнопку или видео с этим текстом;
  - `[SCROLL_DOWN]` и `[SCROLL_UP]` — прокрутить страницу.
- **Две модели с запасным вариантом.** Основной провайдер — OpenAI-совместимый endpoint; если он не ответил, запрос уходит к бесплатному Pollinations.
- **Корпоративный монитор** (`CorporateMonitor`): блокировка выбранных доменов и журнал посещений.

## Запуск

Нужен Python 3.10+.

```bash
pip install PyQt6 PyQt6-WebEngine requests
python main.py
```

## Устройство

| Файл | Назначение |
|---|---|
| `main.py` | Приложение: окно, вкладки, ИИ-агент (`AILogicThread`), корпоративный монитор |
| `start_page.html` | Стартовая страница ITIS Search |
| `patch_*.py` | Скрипты, которыми вносились правки в `main.py` по ходу разработки |
| `test_api.py`, `test_api2.py` | Проверка доступности ИИ-провайдера |
| `logo.*`, `bg_*.jpg`, `reel.mp4` | Логотип и фоны стартовой страницы |

## 🌐 Часть экосистемы MindTagSystem

ITIS Browser входит в **[MindTagSystem](https://github.com/tagiriskaliev18-hash/MindTagSystem)** — экосистему для программистов, которую создаёт **Тагир Искалиев** ([@tagiriskaliev18-hash](https://github.com/tagiriskaliev18-hash)): своя операционная система, браузер, IDE, ИИ-ядро и приложения, которые работают вместе и которые можно встроить в любое устройство.

**Роль в экосистеме:** браузер экосистемы со встроенным ИИ-агентом (слой «Инструменты разработчика»).

| Слой | Проект | Что делает |
|---|---|---|
| Платформа | [AIsktagOS](https://github.com/tagiriskaliev18-hash/AisktagOS) | Операционная система для разработчиков в стиле macOS на любом железе |
| Инструменты разработчика | [Mind IDE](https://github.com/tagiriskaliev18-hash/Mind-IDE) | Собственная среда разработки, рабочее место программиста |
| Инструменты разработчика | **ITIS Browser** ← вы здесь | Браузер с ИИ-агентом, который сам кликает и листает страницы |
| ИИ-ядро | [AI Duo (multimodel-agent)](https://github.com/tagiriskaliev18-hash/multimodel-agent) | Единый ИИ-шлюз с OpenAI-совместимым API для всех моделей |
| ИИ-ядро | [Antigravity ↔ Claude Code Bridge](https://github.com/tagiriskaliev18-hash/antigravity-claude-bridge) | MCP-мост, который связывает Antigravity, Claude Code и пул моделей |
| ИИ-ядро | [Qwen 14B Coder Dev](https://github.com/tagiriskaliev18-hash/qwen14b-coder-dev) | Локальная офлайн-модель для программирования в Ollama |
| Приложения | [FileHub AI](https://github.com/tagiriskaliev18-hash/filehub-ai) | Хранилище файлов с ИИ-агентом для Word, PowerPoint и Excel |
| Приложения | [SortApp (анализатор логов)](https://github.com/tagiriskaliev18-hash/sortapp) | Анализатор журналов доступа к сетевым папкам с отчётами Excel |
| Приложения | [ИИ Доктор (medical-ai-assistant)](https://github.com/tagiriskaliev18-hash/medical-ai-assistant) | Офлайн-ассистент врача приёмного покоя |

Как проекты связаны между собой: [архитектура MindTagSystem](https://github.com/tagiriskaliev18-hash/MindTagSystem/blob/main/docs/ARCHITECTURE.md). Автор всех проектов экосистемы — Тагир Искалиев.
