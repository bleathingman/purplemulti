from __future__ import annotations

import ctypes
import hashlib
import os
import tempfile
import weakref

from PySide6.QtCore import QEvent, QObject, QPoint, Qt, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPalette, QPixmap, QPolygon
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QMenu
from shiboken6 import isValid

from features import settings_store
from features.color_themes import mix
from features.theme_library import ThemeLibrary
from features.theme_model import Theme, validate_theme
from utils import icons
lazy from utils.theme_background import BackgroundRenderer


STATUS_COLORS = {
    'SUCCESS': '#2ECC71', 'WARNING': '#E8A020', 'ERROR': '#EF7676',
    'DANGER_SURFACE': '#5A2A2A', 'ON_DANGER': '#FFFFFF',
    'SUCCESS_SURFACE': '#1E4D1E', 'SUCCESS_BORDER': '#2E6D2E',
}
_arrows = {}
_DWMWA_USE_IMMERSIVE_DARK_MODE = 20
_DWMWA_WINDOW_CORNER_PREFERENCE = 33
_DWMWA_CAPTION_COLOR = 35
_DWMWCP_ROUND = 2
_TOGGLE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="20" viewBox="0 0 36 20">'
    '<rect width="36" height="20" rx="10" fill="{track}"/>'
    '<circle cx="{knob_x}" cy="10" r="7" fill="{knob}"/></svg>'
)


def _svg_asset(svg):
    name = hashlib.sha256(svg.encode('utf-8')).hexdigest()[:16]
    path = os.path.join(tempfile.gettempdir(), f'ram_{name}.svg')
    if not os.path.isfile(path):
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(svg)
    return path.replace('\\', '/')


def _toggle_path(track, knob, knob_x):
    return _svg_asset(_TOGGLE.format(track=track, knob=knob, knob_x=knob_x))


def _soft_tones(colors):
    base = colors['BG']
    return {
        f'{role}_SOFT': mix(base, colors[role], 0.16)
        for role in ('SUCCESS', 'WARNING', 'ERROR')
    }


def style_window_frame(window, caption):
    """Match the native title bar and window corners to the theme."""
    if QGuiApplication.platformName() != 'windows':
        return
    try:
        handle = ctypes.c_void_p(int(window.winId()))
        color = QColor(caption)
        for attribute, value in (
            (_DWMWA_USE_IMMERSIVE_DARK_MODE, 1),
            (_DWMWA_WINDOW_CORNER_PREFERENCE, _DWMWCP_ROUND),
            (_DWMWA_CAPTION_COLOR, color.red() | color.green() << 8 | color.blue() << 16),
        ):
            data = ctypes.c_int(value)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                handle, attribute, ctypes.byref(data), ctypes.sizeof(data),
            )
    except (AttributeError, OSError, RuntimeError):
        pass


def _arrow_path(value):
    path = _arrows.get(value)
    if path and os.path.isfile(path):
        return path
    path = os.path.join(tempfile.gettempdir(), f'ram_arrow_{value.strip("#")}.png')
    pixmap = QPixmap(10, 10)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(value))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPolygon(QPolygon([QPoint(1, 3), QPoint(9, 3), QPoint(5, 8)]))
    painter.end()
    pixmap.save(path, 'PNG')
    _arrows[value] = path.replace('\\', '/')
    return _arrows[value]


def resolve_startup_theme(settings=None):
    return ThemeLibrary().startup(settings_store.load() if settings is None else settings)


class ThemeManager(QObject):
    changed = Signal(object)
    failed = Signal(str)

    def __init__(self, app, library=None):
        super().__init__(app)
        self.app = app
        self.library = library if library is not None else ThemeLibrary()
        self.theme = self.library.startup(settings_store.load()).clone()
        self._styles = weakref.WeakKeyDictionary()
        self._icons = weakref.WeakKeyDictionary()
        self._paints = weakref.WeakSet()
        self._foregrounds = {}
        self._placeholders = weakref.WeakKeyDictionary()
        self._placeholder_cache = {}
        self._windows = weakref.WeakSet()
        self._media_available = True
        self.background = BackgroundRenderer(self)
        self.background.failed.connect(self._media_failed)
        self._closed = False
        self._apply_palette()
        self.background.configure(self.theme.background)
        app.installEventFilter(self)

    @property
    def colors(self):
        colors = {**STATUS_COLORS, **self.theme.colors}
        return {**colors, **_soft_tones(colors)}

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.Show
            and isinstance(watched, (QMainWindow, QDialog))
            and not self._closed
        ):
            style_window_frame(watched, self.colors['BG'])
        return False

    def register(self, window):
        if self._closed or not isValid(window) or isinstance(window, QMenu):
            return
        if isinstance(window, (QMainWindow, QDialog)):
            self._windows.add(window)
            self.background.register(window)

    def apply(self, theme: Theme):
        if self._closed:
            return
        validate_theme(theme)
        old_background = self.theme.background
        old_colors = self.theme.colors
        self.theme = theme.clone()
        colors_changed = old_colors != self.theme.colors
        if colors_changed:
            self._apply_palette()
        if self.theme.background != old_background:
            self._media_available = True
            self.background.configure(self.theme.background)
        for widget, template in list(self._styles.items()):
            if isValid(widget):
                self._update_style(widget, template)
        if colors_changed:
            for button, (name, size, tone) in list(self._icons.items()):
                if isValid(button):
                    icons.set_button_icon(button, name, self.colors, size, tone)
            self._placeholder_cache.clear()
            for label, (size, text, previous_key) in list(self._placeholders.items()):
                if not isValid(label):
                    continue
                if label.pixmap().cacheKey() != previous_key:
                    self._placeholders.pop(label, None)
                    continue
                self.bind_placeholder(label, size, text)
        for widget in list(self._paints):
            if isValid(widget):
                widget.update()
        for reference, role in list(self._foregrounds.values()):
            item = reference()
            if item is not None and isValid(item):
                item.setForeground(QColor(self.colors[role]))
        for window in list(self._windows):
            if isValid(window):
                window.update()
        self.changed.emit(self.theme.clone())

    def activate(self, theme: Theme):
        self.library.activate(theme.id)
        self.apply(theme)

    def render(self, template, widget=None):
        palette = self.colors
        media = self._media_available and self.theme.background.enabled and bool(self.theme.background.path)
        opaque = isinstance(widget, QMenu) or (
            widget is not None and widget.window().windowType() == Qt.WindowType.Popup
        )
        surfaces = {'BG': 60, 'PANEL': 160, 'INPUT': 180, 'RAISED': 185,
                    'SELECT': 215, 'HOVER': 225, 'PRESSED': 225}
        result = str(template)
        for role in ('PANEL', 'SELECT', 'INPUT'):
            result = result.replace(f'@RAM_OPAQUE_{role}@', palette[role])
        if '@RAM_ARROW@' in result:
            result = result.replace('@RAM_ARROW@', _arrow_path(palette['MUTED']))
        if '@RAM_TOGGLE_' in result:
            result = result.replace(
                '@RAM_TOGGLE_ON@', _toggle_path(palette['ACCENT'], palette['ON_ACCENT'], 26)
            ).replace(
                '@RAM_TOGGLE_OFF@', _toggle_path(palette['HOVER'], palette['MUTED'], 10)
            ).replace(
                '@RAM_TOGGLE_DISABLED@', _toggle_path(palette['INPUT'], palette['LINE'], 10)
            )
        for role, value in palette.items():
            if media and not opaque and role in surfaces:
                tint = QColor(value)
                value = f'rgba({tint.red()}, {tint.green()}, {tint.blue()}, {surfaces[role]})'
            result = result.replace(f'@RAM_{role}@', value)
        return result

    def bind_style(self, widget, template):
        if not isValid(widget):
            return
        self._styles[widget] = str(template)
        self.register(widget.window())
        self._update_style(widget, template)

    def _update_style(self, widget, template):
        rendered = self.render(template, widget)
        if widget.styleSheet() != rendered:
            widget.setStyleSheet(rendered)

    def _media_failed(self, detail):
        self._media_available = False
        for widget, template in list(self._styles.items()):
            if isValid(widget):
                self._update_style(widget, template)
        issues = getattr(self.library, 'issues', None)
        if issues is not None and detail not in issues:
            issues.append(detail)
        self.failed.emit(detail)

    def style_template(self, widget):
        return self._styles.get(widget, widget.styleSheet())

    def bind_icon(self, button, name, size=16, tone=None):
        self._icons[button] = (name, size, tone)
        icons.set_button_icon(button, name, self.colors, size, tone)

    def bind_paint(self, widget):
        self._paints.add(widget)

    def bind_foreground(self, item, role):
        key = id(item)
        reference = weakref.ref(item, lambda unused: self._foregrounds.pop(key, None))
        self._foregrounds[key] = (reference, role)
        item.setForeground(QColor(self.colors[role]))

    def placeholder_pixmap(self, size, text=""):
        key = (size, text)
        if key not in self._placeholder_cache:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(self.colors['SELECT']))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            if text:
                font = QFont(painter.font())
                font.setPixelSize(max(8, round(size * 0.36)))
                font.setWeight(QFont.Weight.DemiBold)
                painter.setFont(font)
                painter.setPen(QColor(self.colors['ACCENT_TEXT']))
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
            painter.end()
            self._placeholder_cache[key] = pixmap
        return self._placeholder_cache[key]

    def bind_placeholder(self, label, size, text=""):
        pixmap = self.placeholder_pixmap(size, text)
        label.setPixmap(pixmap)
        self._placeholders[label] = (size, text, pixmap.cacheKey())

    def _apply_palette(self):
        c = self.colors
        p = QPalette()
        roles = {
            'Window': 'BG', 'WindowText': 'TEXT', 'Base': 'INPUT',
            'AlternateBase': 'PANEL', 'Text': 'TEXT', 'Button': 'INPUT',
            'ButtonText': 'TEXT', 'ToolTipBase': 'PANEL', 'ToolTipText': 'TEXT',
            'Highlight': 'SELECT', 'HighlightedText': 'TEXT', 'Link': 'ACCENT_TEXT',
            'PlaceholderText': 'MUTED', 'BrightText': 'ON_ACCENT',
        }
        for role, key in roles.items():
            p.setColor(getattr(QPalette.ColorRole, role), QColor(c[key]))
        for role in ('WindowText', 'Text', 'ButtonText'):
            p.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, role), QColor(c['MUTED']))
        self.app.setPalette(p)

    def close(self):
        if self._closed:
            return
        self._closed = True
        self.background.close()
        self._styles.clear()
        self._icons.clear()
        self._paints.clear()
        self._foregrounds.clear()
        self._placeholders.clear()
        self._placeholder_cache.clear()
        self._windows.clear()
        self.deleteLater()


def get_manager():
    app = QApplication.instance()
    if app is None:
        raise RuntimeError('Create QApplication before using the theme manager.')
    manager = getattr(app, '_ram_theme_manager', None)
    if manager is None or manager._closed:
        manager = ThemeManager(app)
        app._ram_theme_manager = manager
    return manager


def colors():
    app = QApplication.instance()
    manager = getattr(app, '_ram_theme_manager', None) if app else None
    if manager is not None and not manager._closed:
        return manager.colors
    return {**STATUS_COLORS, **resolve_startup_theme().colors}


def color(role):
    return colors()[role]


def bind_style(widget, template):
    get_manager().bind_style(widget, template)


def bind_icon(button, name, size=16, tone=None):
    get_manager().bind_icon(button, name, size, tone)


def bind_paint(widget):
    get_manager().bind_paint(widget)


def bind_foreground(item, role):
    get_manager().bind_foreground(item, role)


def bind_placeholder(label, size, text=""):
    get_manager().bind_placeholder(label, size, text)


def placeholder_pixmap(size, text=""):
    return get_manager().placeholder_pixmap(size, text)


def palette(app):
    get_manager()._apply_palette()
