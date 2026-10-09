"""Связь ITIS Browser с экосистемой MindTagSystem через MindKit.

* Handoff: открытая вкладка отправляется на другие свои устройства, а ссылки,
  пришедшие с них, открываются здесь одним кликом.
* ИИ-ядро: если основной сервис не ответил, вопрос уходит в шлюз AI Duo или
  локальную Ollama (настройки ``mindkit config``), и только потом в Pollinations.

MindKit не обязателен: pip install git+https://github.com/tagiriskaliev18-hash/MindTagSystem
"""
from __future__ import annotations

try:
    from mindkit import assistant, link
except ImportError:  # браузер работает и без экосистемы
    assistant = link = None


def available() -> bool:
    return link is not None


def ask(messages: list[dict]) -> str:
    """Ответ модели из ИИ-ядра экосистемы или пустая строка."""
    if assistant is None:
        return ""
    try:
        return assistant.chat(messages, timeout=25)["text"].strip()
    except Exception:  # noqa: BLE001 — шлюз не запущен: пусть отвечает следующий
        return ""


def send_url(url: str, title: str) -> str:
    """Отправляет вкладку на свои устройства. Возвращает текст для пользователя."""
    if link is None:
        return "MindKit не установлен: pip install git+https://github.com/tagiriskaliev18-hash/MindTagSystem"
    if link.account_key() is None:
        return "MindLink не настроен: mindkit link init (или mindkit link join КЛЮЧ)"
    try:
        res = link.handoff(link.make_activity("url", title or url, url=url, app="itis-browser"))
    except link.LinkError as e:
        return str(e)
    if not res:
        return "Нет известных устройств: mindkit link devices --scan"
    ok = [name for name, state in res.items() if state == "ok"]
    bad = [f"{name} ({state})" for name, state in res.items() if state != "ok"]
    return ("Вкладка отправлена: " + ", ".join(ok) if ok else "") + (" Не доставлено: " + "; ".join(bad) if bad else "")


def incoming(limit: int = 6) -> list[dict]:
    """Последние ссылки, пришедшие с других устройств."""
    if link is None:
        return []
    return [a for a in link.inbox() if a.get("kind") == "url" and a.get("url")][:limit]
