BG = '@RAM_BG@'
PANEL = '@RAM_PANEL@'
INPUT = '@RAM_INPUT@'
TEXT = '@RAM_TEXT@'
MUTED = '@RAM_MUTED@'
LINE = '@RAM_LINE@'
SELECT = '@RAM_SELECT@'
NOTE = '@RAM_NOTE@'
FG_ACCENT = '@RAM_ACCENT@'
HOVER = '@RAM_HOVER@'
PRESSED = '@RAM_PRESSED@'
RAISED = '@RAM_RAISED@'
ACCENT_HOVER = '@RAM_ACCENT_HOVER@'
ACCENT_PRESSED = '@RAM_ACCENT_PRESSED@'
ACCENT_BRIGHT = '@RAM_ACCENT_BRIGHT@'
ACCENT_SOFT = '@RAM_ACCENT_SOFT@'
ACCENT_TEXT = '@RAM_ACCENT_TEXT@'
ACCENT_DEEP = '@RAM_ACCENT_DEEP@'
ON_ACCENT = '@RAM_ON_ACCENT@'
SUCCESS = '@RAM_SUCCESS@'
WARNING = '@RAM_WARNING@'
ERROR = '@RAM_ERROR@'
SUCCESS_SOFT = '@RAM_SUCCESS_SOFT@'
WARNING_SOFT = '@RAM_WARNING_SOFT@'
ERROR_SOFT = '@RAM_ERROR_SOFT@'
DANGER_SURFACE = '@RAM_DANGER_SURFACE@'
ON_DANGER = '@RAM_ON_DANGER@'

ARROW = '@RAM_ARROW@'
TOGGLE_ON = '@RAM_TOGGLE_ON@'
TOGGLE_OFF = '@RAM_TOGGLE_OFF@'
TOGGLE_DISABLED = '@RAM_TOGGLE_DISABLED@'
SUCCESS_SURFACE = '@RAM_SUCCESS_SURFACE@'
SUCCESS_BORDER = '@RAM_SUCCESS_BORDER@'
OPAQUE_PANEL = '@RAM_OPAQUE_PANEL@'
OPAQUE_SELECT = '@RAM_OPAQUE_SELECT@'

FONT = "'Segoe UI Variable Text', 'Segoe UI'"
RADIUS = 8
RADIUS_CARD = 14


# Every control, shared by the main window, detached pages and dialogs.
CONTROLS = f"""
            QWidget {{ color: {TEXT}; font-family: {FONT}; font-size: 13px; }}

            QLabel#pageTitle {{ font-size: 22px; font-weight: 700; }}
            QLabel#pageSubtitle {{ color: {MUTED}; }}
            QLabel#sectionTitle {{ font-size: 15px; font-weight: 600; }}
            QLabel#sectionLabel {{
                color: {MUTED}; font-size: 11px; font-weight: 700;
                letter-spacing: 1px; margin-top: 14px;
            }}
            QLabel#fieldLabel {{ color: {MUTED}; font-size: 12px; }}
            QLabel#caption {{ color: {MUTED}; font-size: 12px; }}
            QLabel#emptyTitle {{ font-size: 14px; font-weight: 600; }}
            QLabel#formError {{ color: {ERROR}; font-size: 12px; }}
            QWidget#emptyState, QWidget#emptyState QLabel {{ background: transparent; }}

            QPushButton#optionCard {{
                background: {INPUT}; border: 1px solid {LINE};
                border-radius: {RADIUS}px; padding: 0; min-height: 0; text-align: left;
            }}
            QPushButton#optionCard:hover {{ background: {RAISED}; border-color: {HOVER}; }}
            QPushButton#optionCard:checked {{ background: {ACCENT_DEEP}; border-color: {FG_ACCENT}; }}
            QPushButton#optionCard QLabel {{ background: transparent; }}
            QLabel#optionTitle {{ font-size: 14px; font-weight: 600; }}

            QLabel#chip {{
                border-radius: 10px; padding: 3px 10px;
                font-size: 12px; font-weight: 600;
                color: {MUTED}; background: {INPUT};
            }}
            QLabel#chip[tone="success"] {{ color: {SUCCESS}; background: {SUCCESS_SOFT}; }}
            QLabel#chip[tone="warning"] {{ color: {WARNING}; background: {WARNING_SOFT}; }}
            QLabel#chip[tone="error"] {{ color: {ERROR}; background: {ERROR_SOFT}; }}
            QLabel#chip[tone="accent"] {{ color: {ACCENT_TEXT}; background: {ACCENT_DEEP}; }}

            QFrame#card {{
                background: {PANEL}; border: 1px solid {LINE};
                border-radius: {RADIUS_CARD}px;
            }}

            QPushButton, QToolButton {{
                background: {INPUT}; border: 1px solid {LINE};
                border-radius: {RADIUS}px; min-height: 32px; padding: 0 12px;
                font-size: 13px; color: {TEXT};
            }}
            QPushButton:hover, QToolButton:hover {{ background: {RAISED}; border-color: {HOVER}; }}
            QPushButton:pressed, QToolButton:pressed {{ background: {PRESSED}; }}
            QPushButton:checked {{ background: {ACCENT_DEEP}; border-color: {ACCENT_SOFT}; }}

            QPushButton[variant="primary"] {{
                background: {FG_ACCENT}; border: 1px solid {FG_ACCENT};
                color: {ON_ACCENT}; font-weight: 600;
            }}
            QPushButton[variant="primary"]:hover {{ background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
            QPushButton[variant="primary"]:pressed {{ background: {ACCENT_PRESSED}; border-color: {ACCENT_PRESSED}; }}
            QPushButton[variant="primary"]:disabled {{ background: {RAISED}; border-color: {RAISED}; color: {MUTED}; }}

            QPushButton[variant="ghost"] {{ background: transparent; border-color: transparent; color: {MUTED}; }}
            QPushButton[variant="ghost"]:hover {{ background: {RAISED}; color: {TEXT}; }}

            QPushButton[variant="danger"] {{ background: {ERROR_SOFT}; border-color: transparent; color: {ERROR}; }}
            QPushButton[variant="danger"]:hover {{ background: {DANGER_SURFACE}; color: {ON_DANGER}; }}

            QPushButton[variant="icon"] {{
                background: transparent; border-color: transparent;
                min-height: 32px; min-width: 32px; max-width: 32px; padding: 0;
            }}
            QPushButton[variant="icon"]:hover {{ background: {RAISED}; }}

            QPushButton#segTab {{
                background: transparent; border: 0; border-radius: 7px;
                min-height: 30px; padding: 0 14px; color: {MUTED};
            }}
            QPushButton#segTab:hover {{ color: {TEXT}; }}
            QPushButton#segTab:checked {{ background: {SELECT}; color: {TEXT}; font-weight: 600; }}
            QPushButton#segTab:focus {{ border: 0; }}
            QFrame#segBar {{
                background: {PANEL}; border: 1px solid {LINE}; border-radius: 10px;
            }}

            QPushButton#groupTab {{
                background: transparent; border: 1px solid {LINE};
                border-radius: 13px; min-height: 24px; max-height: 24px;
                padding: 0 12px; font-size: 12px; color: {MUTED};
            }}
            QPushButton#groupTab:hover {{ background: {RAISED}; color: {TEXT}; }}
            QPushButton#groupTab:checked {{
                background: {ACCENT_DEEP}; border-color: {ACCENT_SOFT};
                color: {ACCENT_TEXT}; font-weight: 600;
            }}

            QToolButton#splitArrow {{
                min-width: 32px; max-width: 32px; padding: 0;
            }}
            QToolButton#splitArrow::menu-indicator {{ image: none; }}

            QLineEdit {{
                background: {INPUT}; border: 1px solid {LINE};
                border-radius: {RADIUS}px; padding: 0 10px; min-height: 32px;
                color: {TEXT}; selection-background-color: {FG_ACCENT};
                selection-color: {ON_ACCENT};
            }}
            QLineEdit:hover {{ border-color: {HOVER}; }}
            QLineEdit QToolButton {{ background: transparent; border: 0; min-height: 0; padding: 0; }}
            QTextEdit, QPlainTextEdit {{
                background: {INPUT}; border: 1px solid {LINE};
                border-radius: {RADIUS}px; color: {TEXT}; padding: 6px;
                selection-background-color: {FG_ACCENT}; selection-color: {ON_ACCENT};
            }}

            QListWidget, QListView, QTreeView, QTableView, QTableWidget {{
                background: {PANEL}; border: 1px solid {LINE};
                border-radius: {RADIUS_CARD}px; outline: none; padding: 6px;
                alternate-background-color: {PANEL};
            }}
            QListWidget::item {{ min-height: 30px; padding-left: 8px; border-radius: {RADIUS}px; }}
            QListWidget::item:hover {{ background: {RAISED}; }}
            QListWidget::item:selected {{ background: {ACCENT_DEEP}; color: {TEXT}; }}
            QHeaderView {{ background: transparent; }}
            QHeaderView::section {{
                background: transparent; border: 0; border-bottom: 1px solid {LINE};
                padding: 6px 8px; color: {MUTED}; font-size: 12px; font-weight: 600;
            }}
            QTableView::item, QTreeView::item {{ padding: 4px; }}
            QTableView::item:selected, QTreeView::item:selected {{ background: {ACCENT_DEEP}; color: {TEXT}; }}

            QLabel#accountName {{ color: {TEXT}; font-size: 13px; font-weight: 600; }}
            QLabel#noteText {{
                color: {NOTE}; background: {ACCENT_DEEP}; border-radius: 9px;
                font-size: 12px; font-weight: 600; padding: 1px 9px;
            }}
            QLabel#performanceSep {{ color: {LINE}; font-size: 12px; }}
            QLabel#ramUsage {{ color: {ACCENT_TEXT}; font-size: 12px; }}
            QLabel#cpuUsage {{ color: {SUCCESS}; font-size: 12px; }}

            QMenu {{
                background: {OPAQUE_PANEL}; border: 1px solid {LINE};
                color: {TEXT}; font-size: 13px; padding: 6px;
            }}
            QMenu::item {{ padding: 7px 26px 7px 12px; border-radius: 6px; }}
            QMenu::item:selected {{ background: {OPAQUE_SELECT}; }}
            QMenu::item:disabled {{ color: {MUTED}; }}
            QMenu::separator {{ height: 1px; background: {LINE}; margin: 5px 6px; }}

            QToolTip {{
                background: {OPAQUE_PANEL}; border: 1px solid {LINE};
                color: {TEXT}; padding: 6px 8px; font-size: 12px;
            }}

            QScrollArea#groupScroll {{ background: transparent; border: 0; }}
            QScrollArea#groupScroll > QWidget > QWidget {{ background: transparent; }}

            QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
            QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
            QScrollBar::handle:vertical {{ background: {HOVER}; border-radius: 3px; min-height: 28px; }}
            QScrollBar::handle:horizontal {{ background: {HOVER}; border-radius: 3px; min-width: 28px; }}
            QScrollBar::handle:hover {{ background: {MUTED}; }}
            QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; border: 0; background: transparent; }}
            QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

            QCheckBox {{ color: {TEXT}; spacing: 10px; min-height: 24px; }}
            QCheckBox::indicator {{ width: 36px; height: 20px; image: url({TOGGLE_OFF}); }}
            QCheckBox::indicator:checked {{ image: url({TOGGLE_ON}); }}
            QCheckBox::indicator:disabled {{ image: url({TOGGLE_DISABLED}); }}
            QCheckBox:disabled {{ color: {MUTED}; }}

            QRadioButton {{ color: {TEXT}; spacing: 8px; min-height: 24px; }}
            QRadioButton::indicator {{
                width: 14px; height: 14px; border-radius: 8px;
                border: 1px solid {HOVER}; background: {INPUT};
            }}
            QRadioButton::indicator:checked {{
                background: {ACCENT_BRIGHT}; border: 4px solid {INPUT};
                width: 8px; height: 8px;
            }}
            QRadioButton:disabled {{ color: {MUTED}; }}

            QGroupBox {{
                border: 1px solid {LINE}; border-radius: {RADIUS_CARD}px;
                margin-top: 12px; padding-top: 8px;
                font-size: 12px; font-weight: 700; color: {MUTED};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 6px; left: 12px;
            }}

            QProgressBar {{
                background: {INPUT}; border: 0; border-radius: 4px;
                text-align: center; font-size: 11px; max-height: 14px;
            }}
            QProgressBar::chunk {{ background: {FG_ACCENT}; border-radius: 4px; }}
        """


MAIN = f"""
            QMainWindow {{ background: {BG}; }}
            {CONTROLS}

            QFrame#navPanel {{ background: {PANEL}; border: 0; border-right: 1px solid {LINE}; }}
            QFrame#centerPanel, QFrame#settingsPanel {{ background: transparent; border: 0; }}
            QFrame#rightPanel {{
                background: {PANEL}; border: 1px solid {LINE};
                border-radius: {RADIUS_CARD}px;
            }}
            QFrame#titleBar {{ background: transparent; border: 0; }}

            QLabel#brandName {{ font-size: 16px; font-weight: 700; }}

            QPushButton#titleButton, QPushButton#closeButton {{
                background: transparent; border: 0; border-radius: 6px;
                min-height: 28px; max-height: 28px; min-width: 36px; padding: 0;
            }}
            QPushButton#titleButton:hover {{ background: {SELECT}; }}
            QPushButton#closeButton:hover {{ background: {DANGER_SURFACE}; }}
            QPushButton#titleButton:focus, QPushButton#closeButton:focus {{ border: 0; }}

            QPushButton#navTab {{
                background: transparent; border: 1px solid transparent;
                border-radius: {RADIUS}px; text-align: left; min-height: 36px;
                padding: 0 10px; color: {MUTED}; font-size: 13px;
            }}
            QPushButton#navTab:hover {{ background: {RAISED}; color: {TEXT}; }}
            QPushButton#navTab:checked {{
                background: {ACCENT_DEEP}; color: {TEXT}; font-weight: 600;
            }}
            QPushButton#navTab:focus {{ border: 1px solid transparent; }}
        """


COMMON = (
    'QPushButton:disabled, QToolButton:disabled { color: @RAM_MUTED@; }'
    'QPushButton:focus, QToolButton:focus, QLineEdit:focus, QComboBox:focus,'
    'QTextEdit:focus { border: 1px solid @RAM_ACCENT@; }'
    'QComboBox { background: @RAM_INPUT@; color: @RAM_TEXT@;'
    ' border: 1px solid @RAM_LINE@; border-radius: 8px; padding: 0 10px; min-height: 32px; }'
    'QComboBox:hover { border-color: @RAM_HOVER@; }'
    'QComboBox::drop-down { border: 0; width: 26px; }'
    'QComboBox::down-arrow { image: url(@RAM_ARROW@); width: 12px; height: 12px; }'
    'QAbstractSpinBox { background: @RAM_INPUT@; color: @RAM_TEXT@; min-height: 32px;'
    ' border: 1px solid @RAM_LINE@; border-radius: 8px; padding: 0 8px; }'
    'QAbstractSpinBox:hover { border-color: @RAM_HOVER@; }'
    'QAbstractSpinBox:focus { border-color: @RAM_ACCENT@; }'
    # Styled spin boxes collapse their editor to 1px unless the buttons sit on the border box.
    'QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {'
    ' subcontrol-origin: border; width: 0; border: 0; }'
    'QComboBox QLineEdit, QAbstractSpinBox QLineEdit { background: transparent;'
    ' border: 0; padding: 0; margin: 0; min-height: 0; min-width: 0; }'
    'QComboBox QAbstractItemView { background: @RAM_OPAQUE_PANEL@; color: @RAM_TEXT@;'
    ' border: 1px solid @RAM_LINE@; padding: 4px; outline: none;'
    ' selection-background-color: @RAM_OPAQUE_SELECT@; selection-color: @RAM_TEXT@; }'
    'QSlider::groove:horizontal { height: 4px; background: @RAM_LINE@; border-radius: 2px; }'
    'QSlider::sub-page:horizontal { background: @RAM_ACCENT@; border-radius: 2px; }'
    'QSlider::handle:horizontal { width: 14px; margin: -5px 0; border-radius: 7px; background: @RAM_ACCENT_BRIGHT@; }'
    'QScrollArea { background: transparent; border: 0; }'
)


DIALOG = f"""
    QDialog {{ background: {BG}; }}
    {CONTROLS}
    QPushButton {{ padding: 0 16px; }}
    QTextEdit {{ font-family: Consolas, monospace; font-size: 12px; }}
""" + COMMON
