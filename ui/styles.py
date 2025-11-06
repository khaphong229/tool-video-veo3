"""
Styles và themes cho ứng dụng Veo3 Video Generator
Chứa dark theme và các style tùy chỉnh cho PyQt6
"""

# ===== DARK THEME STYLESHEET =====

DARK_THEME = """
/* ===== GLOBAL STYLES ===== */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 9pt;
}

/* ===== MAIN WINDOW ===== */
QMainWindow {
    background-color: #1e1e1e;
}

QMainWindow::separator {
    background: #3c3c3c;
    width: 1px;
    height: 1px;
}

/* ===== MENU BAR ===== */
QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-bottom: 1px solid #3c3c3c;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #3c3c3c;
}

QMenuBar::item:pressed {
    background-color: #4c4c4c;
}

/* ===== MENU ===== */
QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    padding: 4px;
}

QMenu::item {
    padding: 6px 30px 6px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0d7377;
}

QMenu::separator {
    height: 1px;
    background: #3c3c3c;
    margin: 4px 10px;
}

QMenu::icon {
    padding-left: 10px;
}

/* ===== TOOLBAR ===== */
QToolBar {
    background-color: #2d2d2d;
    border: none;
    border-bottom: 1px solid #3c3c3c;
    padding: 4px;
    spacing: 6px;
}

QToolBar::separator {
    background-color: #3c3c3c;
    width: 1px;
    margin: 4px 2px;
}

QToolButton {
    background-color: transparent;
    color: #e0e0e0;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
}

QToolButton:hover {
    background-color: #3c3c3c;
}

QToolButton:pressed {
    background-color: #0d7377;
}

QToolButton:checked {
    background-color: #0d7377;
}

/* ===== STATUS BAR ===== */
QStatusBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border-top: 1px solid #3c3c3c;
}

QStatusBar::item {
    border: none;
}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    background-color: #1e1e1e;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #a0a0a0;
    border: 1px solid #3c3c3c;
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #14ffec;
    border-bottom: 2px solid #14ffec;
}

QTabBar::tab:hover:!selected {
    background-color: #3c3c3c;
    color: #e0e0e0;
}

/* ===== BUTTONS ===== */
QPushButton {
    background-color: #0d7377;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #14a085;
}

QPushButton:pressed {
    background-color: #0a5d61;
}

QPushButton:disabled {
    background-color: #3c3c3c;
    color: #6c6c6c;
}

QPushButton#primaryButton {
    background-color: #14ffec;
    color: #000000;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #0dd9cc;
}

QPushButton#dangerButton {
    background-color: #d32f2f;
}

QPushButton#dangerButton:hover {
    background-color: #f44336;
}

QPushButton#secondaryButton {
    background-color: #424242;
    color: #e0e0e0;
}

QPushButton#secondaryButton:hover {
    background-color: #525252;
}

/* ===== TEXT EDIT / PLAIN TEXT EDIT ===== */
QTextEdit, QPlainTextEdit {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #0d7377;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #14ffec;
}

/* ===== LINE EDIT ===== */
QLineEdit {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #0d7377;
}

QLineEdit:focus {
    border: 1px solid #14ffec;
}

QLineEdit:disabled {
    background-color: #2d2d2d;
    color: #6c6c6c;
}

/* ===== COMBO BOX ===== */
QComboBox {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}

QComboBox:hover {
    border: 1px solid #14ffec;
}

QComboBox:focus {
    border: 1px solid #14ffec;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #e0e0e0;
    margin-right: 5px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    selection-background-color: #0d7377;
    outline: none;
}

/* ===== SPIN BOX / DOUBLE SPIN BOX ===== */
QSpinBox, QDoubleSpinBox {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 8px 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #14ffec;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #3c3c3c;
    border-top-right-radius: 6px;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #3c3c3c;
    border-bottom-right-radius: 6px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #4c4c4c;
}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {
    background-color: #3c3c3c;
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: #14ffec;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #0dd9cc;
}

QSlider::sub-page:horizontal {
    background-color: #0d7377;
    border-radius: 3px;
}

/* ===== PROGRESS BAR ===== */
QProgressBar {
    background-color: #252525;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    height: 24px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 #0d7377, stop:1 #14ffec);
    border-radius: 5px;
}

/* ===== GROUP BOX ===== */
QGroupBox {
    background-color: #252525;
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #14ffec;
}

/* ===== SCROLL BAR ===== */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4c4c4c;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5c5c5c;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4c4c4c;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5c5c5c;
}

/* ===== LIST WIDGET / LIST VIEW ===== */
QListWidget, QListView {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    outline: none;
}

QListWidget::item, QListView::item {
    padding: 8px;
    border-radius: 4px;
}

QListWidget::item:selected, QListView::item:selected {
    background-color: #0d7377;
    color: #ffffff;
}

QListWidget::item:hover, QListView::item:hover {
    background-color: #3c3c3c;
}

/* ===== TABLE WIDGET / TABLE VIEW ===== */
QTableWidget, QTableView {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    gridline-color: #3c3c3c;
}

QTableWidget::item, QTableView::item {
    padding: 6px;
}

QTableWidget::item:selected, QTableView::item:selected {
    background-color: #0d7377;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #14ffec;
    padding: 8px;
    border: none;
    border-right: 1px solid #3c3c3c;
    border-bottom: 1px solid #3c3c3c;
    font-weight: 600;
}

/* ===== TREE WIDGET / TREE VIEW ===== */
QTreeWidget, QTreeView {
    background-color: #252525;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    outline: none;
}

QTreeWidget::item, QTreeView::item {
    padding: 6px;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #0d7377;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: #3c3c3c;
}

QTreeWidget::branch:closed:has-children {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #e0e0e0;
}

QTreeWidget::branch:open:has-children {
    image: url(none);
    border-left: 5px solid #e0e0e0;
    border-right: 5px solid transparent;
    border-bottom: 5px solid transparent;
}

/* ===== DOCK WIDGET ===== */
QDockWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}

QDockWidget::title {
    background-color: #2d2d2d;
    padding: 8px;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
}

QDockWidget::close-button, QDockWidget::float-button {
    background-color: #3c3c3c;
    border-radius: 3px;
    padding: 2px;
}

QDockWidget::close-button:hover, QDockWidget::float-button:hover {
    background-color: #4c4c4c;
}

/* ===== SPLITTER ===== */
QSplitter::handle {
    background-color: #3c3c3c;
}

QSplitter::handle:hover {
    background-color: #14ffec;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* ===== LABEL ===== */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 14pt;
    font-weight: 600;
    color: #14ffec;
}

QLabel#subtitleLabel {
    font-size: 10pt;
    color: #a0a0a0;
}

/* ===== CHECKBOX ===== */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3c3c3c;
    border-radius: 4px;
    background-color: #252525;
}

QCheckBox::indicator:hover {
    border: 2px solid #14ffec;
}

QCheckBox::indicator:checked {
    background-color: #14ffec;
    border: 2px solid #14ffec;
    image: url(none);
}

/* ===== RADIO BUTTON ===== */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #3c3c3c;
    border-radius: 9px;
    background-color: #252525;
}

QRadioButton::indicator:hover {
    border: 2px solid #14ffec;
}

QRadioButton::indicator:checked {
    background-color: #14ffec;
    border: 2px solid #14ffec;
}

/* ===== TOOLTIP ===== */
QToolTip {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 1px solid #14ffec;
    border-radius: 4px;
    padding: 6px;
}
"""

# ===== ACCENT COLORS =====
ACCENT_COLORS = {
    'primary': '#14ffec',      # Cyan/Turquoise
    'secondary': '#0d7377',    # Dark cyan
    'danger': '#d32f2f',       # Red
    'warning': '#ffa726',      # Orange
    'success': '#66bb6a',      # Green
    'info': '#42a5f5',         # Blue
}

# ===== ICON PLACEHOLDERS (Unicode symbols) =====
ICONS = {
    'new_project': '📁',
    'open_project': '📂',
    'save': '💾',
    'save_as': '📝',
    'export': '📤',
    'import': '📥',
    'settings': '⚙️',
    'refresh': '🔄',
    'play': '▶️',
    'pause': '⏸️',
    'stop': '⏹️',
    'download': '⬇️',
    'upload': '⬆️',
    'delete': '🗑️',
    'edit': '✏️',
    'add': '➕',
    'remove': '➖',
    'search': '🔍',
    'filter': '🔽',
    'close': '✖️',
    'minimize': '🗕',
    'maximize': '🗖',
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✅',
    'video': '🎬',
    'image': '🖼️',
    'folder': '📁',
    'file': '📄',
    'link': '🔗',
    'copy': '📋',
    'cut': '✂️',
    'paste': '📌',
    'undo': '↶',
    'redo': '↷',
    'zoom_in': '🔍+',
    'zoom_out': '🔍-',
    'fullscreen': '⛶',
    'exit_fullscreen': '⛶',
    'help': '❓',
    'about': 'ℹ️',
    'user': '👤',
    'api': '🔌',
    'database': '🗄️',
    'log': '📋',
    'calendar': '📅',
    'clock': '🕐',
    'star': '⭐',
    'heart': '❤️',
    'bookmark': '🔖',
    'tag': '🏷️',
    'arrow_up': '⬆️',
    'arrow_down': '⬇️',
}

# ===== HELPER FUNCTIONS =====

def get_icon_text(icon_name: str) -> str:
    """
    Lấy icon placeholder từ tên

    Args:
        icon_name: Tên icon

    Returns:
        str: Unicode icon character
    """
    return ICONS.get(icon_name, '●')


def get_accent_color(color_name: str) -> str:
    """
    Lấy mã màu accent

    Args:
        color_name: Tên màu

    Returns:
        str: Mã màu hex
    """
    return ACCENT_COLORS.get(color_name, ACCENT_COLORS['primary'])


# ===== EXPORT =====
__all__ = [
    'DARK_THEME',
    'ACCENT_COLORS',
    'ICONS',
    'get_icon_text',
    'get_accent_color'
]
