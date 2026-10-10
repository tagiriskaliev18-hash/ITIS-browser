"""Эффекты единого стиля Mind для ITIS Browser (PyQt6).

Vendoring: адаптированная копия ``mindkit/qtfx.py`` из MindTagSystem
(https://github.com/tagiriskaliev18-hash/MindTagSystem, docs/DESIGN.md).
Браузер не зависит от MindKit, поэтому иконки берутся из ``mind/icons/*.svg``
(градиент уже внутри файлов), а стопы градиента продублированы здесь.

* ``icon(name)`` — QIcon иконки Mind с фиолетово-синим градиентом
  (``white=True`` — белая, для кнопок с градиентным фоном);
* ``bounce`` / ``bounce_on_hover`` — пружина при наведении и нажатии;
* ``shimmer`` — переливающийся градиент на фоне или тексте виджета.

Анимации отключаются переменной окружения ``MIND_REDUCED_MOTION=1``
(аналог prefers-reduced-motion для настольной программы).
"""
from __future__ import annotations

import os

from PyQt6.QtCore import (QByteArray, QEasingCurve, QEvent, QObject, QPoint,
                          QPropertyAnimation, QSequentialAnimationGroup, Qt,
                          QVariantAnimation)
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.join(HERE, "icons")

# Фиолетово-синий градиент Mind (mindkit/data/tokens.json → gradient.stops)
STOPS = ["#a46cf0", "#7c66df", "#5b8dee", "#49b3f7"]
GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, " + ", ".join(
    f"stop:{round(i / (len(STOPS) - 1), 2)} {c}" for i, c in enumerate(STOPS)) + ")"
REDUCED_MOTION = os.environ.get("MIND_REDUCED_MOTION", "") not in ("", "0")


def stylesheet() -> str:
    """Базовый QSS Aurora из MindKit (design/mind-ui.qss)."""
    with open(os.path.join(HERE, "mind-ui.qss"), encoding="utf-8") as f:
        return f.read()


def _svg(name: str, white: bool) -> bytes:
    with open(os.path.join(ICONS, f"{name}.svg"), encoding="utf-8") as f:
        svg = f.read()
    if white:
        # Белая иконка: обводка цветом вместо ссылки на градиент
        svg = svg.replace(f"stroke='url(#mi-g-{name})'", "stroke='#ffffff'")
    return svg.encode()


def pixmap(name: str, size: int = 48, white: bool = False) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(_svg(name, white)))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    renderer.render(p)
    p.end()
    return pm


def icon(name: str, size: int = 48, white: bool = False) -> QIcon:
    """QIcon иконки Mind с фиолетово-синим градиентом (или белая)."""
    return QIcon(pixmap(name, size, white))


def bounce(widget, height: int = 6, duration: int = 520):
    """Один пружинящий прыжок виджета (появление, уведомление, клик)."""
    if REDUCED_MOTION:
        return None
    start = widget.pos()
    up = QPropertyAnimation(widget, b"pos", widget)
    up.setDuration(duration // 3)
    up.setStartValue(start)
    up.setEndValue(start - QPoint(0, height))
    up.setEasingCurve(QEasingCurve.Type.OutQuad)
    down = QPropertyAnimation(widget, b"pos", widget)
    down.setDuration(duration - duration // 3)
    down.setStartValue(start - QPoint(0, height))
    down.setEndValue(start)
    down.setEasingCurve(QEasingCurve.Type.OutBounce)
    group = QSequentialAnimationGroup(widget)
    group.addAnimation(up)
    group.addAnimation(down)
    group.start()
    widget._mt_bounce = group  # держим ссылку, иначе анимацию соберёт сборщик мусора
    return group


class _BounceFilter(QObject):
    def __init__(self, parent, height):
        super().__init__(parent)
        self.height = height

    def eventFilter(self, obj, ev):  # noqa: N802 — имя из Qt
        if ev.type() in (QEvent.Type.Enter, QEvent.Type.MouseButtonRelease):
            anim = getattr(obj, "_mt_bounce", None)
            if anim is None or anim.state() != anim.State.Running:
                bounce(obj, self.height, 420)
        return False


def bounce_on_hover(widget, height: int = 3):
    """Пружинка при наведении и при нажатии (кнопки, значки)."""
    f = _BounceFilter(widget, height)
    widget.installEventFilter(f)
    widget._mt_bounce_filter = f
    return f


def shimmer(widget, prop: str = "background", period_ms: int = 6000, extra: str = "",
            selector: str = ""):
    """Переливающийся градиент Mind (Qt не умеет CSS-анимации — двигаем стопы сами).

    ``prop`` — свойство QSS (``background`` или ``color`` для текста),
    ``extra`` — остальные правила виджета, ``selector`` — например ``QPushButton``,
    чтобы дописать к нему состояния (``extra`` может содержать их через ``}``).
    """
    parts = ", ".join(f"stop:{round(i / (len(STOPS) - 1), 2)} {c}" for i, c in enumerate(STOPS))

    def paint(v):
        x = float(v)
        rule = (f"{prop}: qlineargradient(x1:{-x:.3f}, y1:0, x2:{1 - x:.3f}, y2:1, "
                f"spread:reflect, {parts}); ")
        if selector:
            widget.setStyleSheet(f"{selector} {{ {rule}{extra}")
        else:
            widget.setStyleSheet(rule + extra)

    paint(0.0)
    if REDUCED_MOTION:
        return None
    anim = QVariantAnimation(widget)
    anim.setStartValue(0.0)
    anim.setKeyValueAt(0.5, 1.0)
    anim.setEndValue(0.0)
    anim.setDuration(period_ms)
    anim.setLoopCount(-1)
    anim.valueChanged.connect(paint)
    anim.start()
    widget._mt_shimmer = anim
    return anim
