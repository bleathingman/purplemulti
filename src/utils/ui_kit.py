"""
Small layout building blocks shared by the application pages.
"""

from __future__ import annotations

import re

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QAbstractButton, QAbstractScrollArea, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

PAGE_MARGINS = (24, 4, 24, 20)


def initials(name: str) -> str:
    """Two letters for an avatar placeholder: "NightOwl_22" -> "NO", "alt_main" -> "AM"."""
    words = re.findall(r"[A-Z]+[a-z]*|[a-z]+|[0-9]+", name or "")
    letters = [word[0] for word in words if not word.isdigit()] or [word[0] for word in words]
    return "".join(letters[:2]).upper()


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_variant(button: QAbstractButton, variant: str) -> QAbstractButton:
    button.setProperty("variant", variant)
    _repolish(button)
    return button


def set_chip(label: QLabel, text: str, tone: str = "") -> None:
    label.setText(text)
    label.setProperty("tone", tone)
    _repolish(label)


def chip(text: str = "", tone: str = "") -> QLabel:
    label = QLabel()
    label.setObjectName("chip")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    set_chip(label, text, tone)
    return label


def caption(text: str = "", wrap: bool = True) -> QLabel:
    label = QLabel(text)
    label.setObjectName("caption")
    label.setWordWrap(wrap)
    return label


def field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("fieldLabel")
    return label


def section_label(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("sectionLabel")
    return label


def card(spacing: int = 12, margins: tuple[int, int, int, int] = (18, 16, 18, 16)) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


class OptionCard(QPushButton):
    """Checkable card with a bold title and a wrapped description; its height follows the text."""

    def __init__(self, title: str, description: str = "", badge: str = ""):
        super().__init__()
        self.setObjectName("optionCard")
        self.setCheckable(True)
        self.setAccessibleName(title)
        self.setAccessibleDescription(description)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)
        heading = QHBoxLayout()
        heading.setSpacing(8)
        name = QLabel(title)
        name.setObjectName("optionTitle")
        heading.addWidget(name)
        if badge:
            heading.addWidget(chip(badge, "accent"))
        heading.addStretch(1)
        layout.addLayout(heading)
        if description:
            layout.addWidget(caption(description))
        for label in self.findChildren(QLabel):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return self.layout().totalHeightForWidth(width)

    def sizeHint(self):
        hint = self.layout().totalSizeHint()
        hint.setHeight(self.heightForWidth(max(hint.width(), self.width())))
        return hint

    def minimumSizeHint(self):
        return self.layout().totalMinimumSize()


def option_card(title: str, description: str = "", badge: str = "") -> OptionCard:
    return OptionCard(title, description, badge)


def page_header(title: str, subtitle: str = "", trailing: QWidget | None = None) -> QVBoxLayout:
    header = QVBoxLayout()
    header.setContentsMargins(0, 0, 0, 0)
    header.setSpacing(2)
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("pageTitle")
    row.addWidget(heading)
    row.addStretch(1)
    if trailing is not None:
        row.addWidget(trailing)
    header.addLayout(row)
    if subtitle:
        line = QLabel(subtitle)
        line.setObjectName("pageSubtitle")
        line.setWordWrap(True)
        header.addWidget(line)
    return header


def form_row(label: str, control, tip: str = "") -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(10)
    text = QLabel(label)
    if tip:
        text.setToolTip(tip)
    row.addWidget(text)
    row.addStretch(1)
    if isinstance(control, QWidget):
        row.addWidget(control)
    else:
        row.addLayout(control)
    return row


class CardFlow:
    """Layout stand-in that groups rows into one card per section label."""

    def __init__(self, layout: QVBoxLayout, spacing: int = 10):
        self._outer = layout
        self._spacing = spacing
        self._card: QVBoxLayout | None = None

    def _target(self) -> QVBoxLayout:
        if self._card is None:
            frame, self._card = card(spacing=self._spacing)
            self._outer.addWidget(frame)
        return self._card

    def addWidget(self, widget: QWidget, *args) -> None:
        if widget.objectName() == "sectionLabel":
            self._outer.addWidget(widget)
            self._card = None
        elif isinstance(widget, QPushButton) and not args:
            self._target().addWidget(widget, 0, Qt.AlignmentFlag.AlignLeft)
        else:
            self._target().addWidget(widget, *args)

    def addLayout(self, layout, *args) -> None:
        self._target().addLayout(layout, *args)

    def addStretch(self, stretch: int = 0) -> None:
        self._outer.addStretch(stretch)

    def addSpacing(self, size: int) -> None:
        self._target().addSpacing(size)


class EmptyState(QWidget):
    """Centered message shown over an empty list or table."""

    def __init__(self, view: QAbstractScrollArea, title: str = "", hint: str = ""):
        super().__init__(view.viewport())
        self.setObjectName("emptyState")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(4)
        layout.addStretch(1)
        self._title = QLabel()
        self._title.setObjectName("emptyTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._hint = caption()
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)
        layout.addWidget(self._hint)
        layout.addStretch(1)
        self._viewport = view.viewport()
        self._viewport.installEventFilter(self)
        self.set_text(title, hint)
        self.setGeometry(self._viewport.rect())
        self.hide()

    def set_text(self, title: str, hint: str = "") -> None:
        self._title.setText(title)
        self._hint.setText(hint)
        self._hint.setVisible(bool(hint))

    def title(self) -> str:
        return self._title.text()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._viewport and event.type() == QEvent.Type.Resize:
            self.setGeometry(self._viewport.rect())
        return False
