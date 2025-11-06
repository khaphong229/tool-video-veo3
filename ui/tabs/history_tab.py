"""
History & Library Tab - View and manage generated videos
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QScrollArea, QFrame,
    QGridLayout, QListWidget, QListWidgetItem, QMenu, QMessageBox,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QButtonGroup, QRadioButton, QSplitter,
    QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QAction, QColor

from utils import get_logger

logger = get_logger(__name__)


class VideoCard(QFrame):
    """Widget representing a single video in grid view"""

    clicked = pyqtSignal(int)  # video_id
    double_clicked = pyqtSignal(int)
    context_menu_requested = pyqtSignal(int, object)  # video_id, QPoint

    def __init__(self, video_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.video_data = video_data
        self.video_id = video_data.get('id', 0)

        self.setup_ui()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Hover effect
        self.setStyleSheet("""
            VideoCard {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            VideoCard:hover {
                border: 2px solid #0078d4;
                background-color: #f5f5f5;
            }
        """)

    def setup_ui(self):
        """Setup video card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Thumbnail
        thumbnail_label = QLabel()
        thumbnail_label.setFixedSize(200, 150)
        thumbnail_label.setScaledContents(True)
        thumbnail_label.setStyleSheet("border: 1px solid #ddd; background-color: #f0f0f0;")

        thumbnail_path = self.video_data.get('thumbnail_path')
        if thumbnail_path and os.path.exists(thumbnail_path):
            pixmap = QPixmap(thumbnail_path)
            thumbnail_label.setPixmap(pixmap)
        else:
            thumbnail_label.setText("No Preview")
            thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(thumbnail_label)

        # Status badge
        status = self.video_data.get('status', 'unknown')
        status_color = {
            'completed': '#28a745',
            'failed': '#dc3545',
            'processing': '#ffc107',
            'pending': '#6c757d'
        }.get(status, '#6c757d')

        status_label = QLabel(status.upper())
        status_label.setStyleSheet(f"""
            background-color: {status_color};
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: bold;
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_label)

        # Prompt (truncated)
        prompt = self.video_data.get('prompt', 'No prompt')
        if len(prompt) > 60:
            prompt = prompt[:60] + '...'

        prompt_label = QLabel(prompt)
        prompt_label.setWordWrap(True)
        prompt_label.setStyleSheet("font-size: 11px; color: #333;")
        layout.addWidget(prompt_label)

        # Metadata
        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)

        # Model
        model = self.video_data.get('model', 'Unknown')
        model_label = QLabel(f"Model: {model}")
        model_label.setStyleSheet("font-size: 10px; color: #666;")
        meta_layout.addWidget(model_label)

        # Date
        created_at = self.video_data.get('created_at', '')
        if created_at:
            try:
                date_obj = datetime.fromisoformat(created_at)
                date_str = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = created_at
        else:
            date_str = 'Unknown'

        date_label = QLabel(f"Date: {date_str}")
        date_label.setStyleSheet("font-size: 10px; color: #666;")
        meta_layout.addWidget(date_label)

        # Duration
        duration = self.video_data.get('duration', 0)
        duration_label = QLabel(f"Duration: {duration}s")
        duration_label.setStyleSheet("font-size: 10px; color: #666;")
        meta_layout.addWidget(duration_label)

        layout.addLayout(meta_layout)
        layout.addStretch()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.video_id)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.video_id)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        """Handle right click"""
        self.context_menu_requested.emit(self.video_id, event.globalPos())


class HistoryTab(QWidget):
    """History & Library Tab for viewing and managing generated videos"""

    # Signals
    video_opened = pyqtSignal(int)  # video_id
    video_deleted = pyqtSignal(int)  # video_id
    video_regenerated = pyqtSignal(dict)  # video_data

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager

        # State
        self.current_view_mode = 'grid'  # 'grid' or 'list'
        self.current_page = 0
        self.page_size = 20
        self.total_videos = 0
        self.all_videos = []  # Cache of all videos
        self.filtered_videos = []  # Currently filtered videos
        self.selected_video_ids = set()  # For bulk operations

        # Current filters
        self.current_filters = {
            'search': '',
            'date_from': None,
            'date_to': None,
            'model': 'All',
            'status': 'All',
            'sort_by': 'date_desc'
        }

        self.setup_ui()
        self.load_history()

        logger.info("History Tab initialized")

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top filter bar
        filter_bar = self.create_filter_bar()
        layout.addWidget(filter_bar)

        # View mode toggle
        view_toggle_bar = self.create_view_toggle_bar()
        layout.addWidget(view_toggle_bar)

        # Main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Grid view (default)
        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(10)
        self.grid_scroll.setWidget(self.grid_widget)

        # List view (table)
        self.list_table = QTableWidget()
        self.list_table.setColumnCount(7)
        self.list_table.setHorizontalHeaderLabels([
            'ID', 'Thumbnail', 'Prompt', 'Model', 'Status', 'Duration', 'Created'
        ])
        self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.list_table.horizontalHeader().setStretchLastSection(True)
        self.list_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.list_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_table.customContextMenuRequested.connect(self.show_table_context_menu)
        self.list_table.doubleClicked.connect(self.on_table_double_click)
        self.list_table.hide()

        self.content_layout.addWidget(self.grid_scroll)
        self.content_layout.addWidget(self.list_table)

        layout.addWidget(self.content_area, 1)

        # Pagination
        pagination_bar = self.create_pagination_bar()
        layout.addWidget(pagination_bar)

        # Bottom actions
        bottom_bar = self.create_bottom_bar()
        layout.addWidget(bottom_bar)

    def create_filter_bar(self) -> QWidget:
        """Create top filter bar"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by prompt or filename...")
        self.search_input.setMinimumWidth(250)
        self.search_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.search_input)

        layout.addSpacing(10)

        # Date range
        layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.on_filter_changed)
        layout.addWidget(self.date_from)

        layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.on_filter_changed)
        layout.addWidget(self.date_to)

        layout.addSpacing(10)

        # Model filter
        layout.addWidget(QLabel("Model:"))
        self.model_filter = QComboBox()
        self.model_filter.addItems(['All', 'veo-2.0', 'veo-1.0'])
        self.model_filter.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.model_filter)

        # Status filter
        layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(['All', 'completed', 'failed', 'processing', 'pending'])
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.status_filter)

        # Sort
        layout.addWidget(QLabel("Sort:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            'Date (Newest First)',
            'Date (Oldest First)',
            'Duration (Longest)',
            'Duration (Shortest)',
            'Name (A-Z)',
            'Name (Z-A)'
        ])
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        layout.addWidget(self.sort_combo)

        layout.addStretch()

        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        layout.addWidget(clear_btn)

        return widget

    def create_view_toggle_bar(self) -> QWidget:
        """Create view mode toggle bar"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)

        layout.addWidget(QLabel("View:"))

        # View mode buttons
        self.grid_view_btn = QRadioButton("Grid")
        self.grid_view_btn.setChecked(True)
        self.grid_view_btn.toggled.connect(lambda checked: self.switch_view_mode('grid') if checked else None)

        self.list_view_btn = QRadioButton("List")
        self.list_view_btn.toggled.connect(lambda checked: self.switch_view_mode('list') if checked else None)

        view_group = QButtonGroup(self)
        view_group.addButton(self.grid_view_btn)
        view_group.addButton(self.list_view_btn)

        layout.addWidget(self.grid_view_btn)
        layout.addWidget(self.list_view_btn)

        layout.addStretch()

        # Results count
        self.results_label = QLabel("0 videos")
        layout.addWidget(self.results_label)

        return widget

    def create_pagination_bar(self) -> QWidget:
        """Create pagination controls"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)

        self.prev_page_btn = QPushButton("◀ Previous")
        self.prev_page_btn.clicked.connect(self.previous_page)
        layout.addWidget(self.prev_page_btn)

        layout.addStretch()

        self.page_label = QLabel("Page 1 of 1")
        layout.addWidget(self.page_label)

        layout.addStretch()

        self.next_page_btn = QPushButton("Next ▶")
        self.next_page_btn.clicked.connect(self.next_page)
        layout.addWidget(self.next_page_btn)

        return widget

    def create_bottom_bar(self) -> QWidget:
        """Create bottom action bar"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)

        # Bulk operations
        bulk_label = QLabel("Bulk Actions:")
        layout.addWidget(bulk_label)

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_videos)
        layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_videos)
        layout.addWidget(deselect_all_btn)

        bulk_delete_btn = QPushButton("Delete Selected")
        bulk_delete_btn.clicked.connect(self.bulk_delete_videos)
        bulk_delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        layout.addWidget(bulk_delete_btn)

        layout.addStretch()

        # Storage info
        self.storage_label = QLabel("Storage: Calculating...")
        layout.addWidget(self.storage_label)

        # Refresh storage info periodically
        QTimer.singleShot(1000, self.update_storage_info)

        layout.addSpacing(20)

        # Clear cache
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        layout.addWidget(clear_cache_btn)

        # Refresh
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_history)
        layout.addWidget(refresh_btn)

        return widget

    def load_history(self, filters: Optional[Dict[str, Any]] = None):
        """
        Load video history from database

        Args:
            filters: Optional filter dictionary
        """
        if filters:
            self.current_filters.update(filters)

        logger.info(f"Loading history with filters: {self.current_filters}")

        # Get all videos from database
        if self.db_manager:
            try:
                self.all_videos = self.db_manager.get_all_videos()
                logger.info(f"Loaded {len(self.all_videos)} videos from database")
            except Exception as e:
                logger.error(f"Failed to load videos from database: {e}")
                self.all_videos = []
        else:
            # Mock data for testing
            self.all_videos = self.generate_mock_data()
            logger.info(f"Using mock data: {len(self.all_videos)} videos")

        # Apply filters
        self.filtered_videos = self.apply_filters(self.all_videos)
        self.total_videos = len(self.filtered_videos)

        # Reset to first page
        self.current_page = 0

        # Display current page
        self.display_current_page()

        # Update UI
        self.update_pagination_ui()
        self.update_results_count()

    def apply_filters(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filters to video list"""
        filtered = videos.copy()

        # Search filter
        search_text = self.current_filters.get('search', '').lower()
        if search_text:
            filtered = [
                v for v in filtered
                if search_text in v.get('prompt', '').lower()
                or search_text in v.get('filename', '').lower()
            ]

        # Date range filter
        date_from = self.current_filters.get('date_from')
        date_to = self.current_filters.get('date_to')

        if date_from:
            date_from_str = date_from.toString('yyyy-MM-dd')
            filtered = [
                v for v in filtered
                if v.get('created_at', '') >= date_from_str
            ]

        if date_to:
            date_to_str = date_to.toString('yyyy-MM-dd') + ' 23:59:59'
            filtered = [
                v for v in filtered
                if v.get('created_at', '') <= date_to_str
            ]

        # Model filter
        model_filter = self.current_filters.get('model', 'All')
        if model_filter != 'All':
            filtered = [v for v in filtered if v.get('model') == model_filter]

        # Status filter
        status_filter = self.current_filters.get('status', 'All')
        if status_filter != 'All':
            filtered = [v for v in filtered if v.get('status') == status_filter]

        # Sort
        sort_by = self.current_filters.get('sort_by', 'date_desc')
        filtered = self.sort_videos(filtered, sort_by)

        return filtered

    def sort_videos(self, videos: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort videos by specified criteria"""
        if sort_by == 'date_desc':
            return sorted(videos, key=lambda v: v.get('created_at', ''), reverse=True)
        elif sort_by == 'date_asc':
            return sorted(videos, key=lambda v: v.get('created_at', ''))
        elif sort_by == 'duration_desc':
            return sorted(videos, key=lambda v: v.get('duration', 0), reverse=True)
        elif sort_by == 'duration_asc':
            return sorted(videos, key=lambda v: v.get('duration', 0))
        elif sort_by == 'name_asc':
            return sorted(videos, key=lambda v: v.get('filename', '').lower())
        elif sort_by == 'name_desc':
            return sorted(videos, key=lambda v: v.get('filename', '').lower(), reverse=True)
        return videos

    def display_current_page(self):
        """Display current page of videos"""
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_videos = self.filtered_videos[start_idx:end_idx]

        if self.current_view_mode == 'grid':
            self.display_grid_view(page_videos)
        else:
            self.display_list_view(page_videos)

    def display_grid_view(self, videos: List[Dict[str, Any]]):
        """Display videos in grid view"""
        # Clear existing grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add video cards
        columns = 4
        for i, video_data in enumerate(videos):
            row = i // columns
            col = i % columns

            card = VideoCard(video_data)
            card.clicked.connect(self.on_video_clicked)
            card.double_clicked.connect(self.on_video_double_clicked)
            card.context_menu_requested.connect(self.show_context_menu)

            self.grid_layout.addWidget(card, row, col)

        # Add stretch to fill remaining space
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

    def display_list_view(self, videos: List[Dict[str, Any]]):
        """Display videos in list/table view"""
        self.list_table.setRowCount(len(videos))

        for row, video_data in enumerate(videos):
            # ID
            id_item = QTableWidgetItem(str(video_data.get('id', '')))
            id_item.setData(Qt.ItemDataRole.UserRole, video_data.get('id'))
            self.list_table.setItem(row, 0, id_item)

            # Thumbnail
            thumbnail_label = QLabel()
            thumbnail_label.setFixedSize(80, 60)
            thumbnail_label.setScaledContents(True)
            thumbnail_path = video_data.get('thumbnail_path')
            if thumbnail_path and os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                thumbnail_label.setPixmap(pixmap)
            else:
                thumbnail_label.setText("No Preview")
                thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumbnail_label.setStyleSheet("background-color: #f0f0f0;")
            self.list_table.setCellWidget(row, 1, thumbnail_label)

            # Prompt
            prompt = video_data.get('prompt', 'No prompt')
            if len(prompt) > 100:
                prompt = prompt[:100] + '...'
            prompt_item = QTableWidgetItem(prompt)
            self.list_table.setItem(row, 2, prompt_item)

            # Model
            model_item = QTableWidgetItem(video_data.get('model', 'Unknown'))
            self.list_table.setItem(row, 3, model_item)

            # Status
            status = video_data.get('status', 'unknown')
            status_item = QTableWidgetItem(status.upper())
            status_color = {
                'completed': QColor(40, 167, 69),
                'failed': QColor(220, 53, 69),
                'processing': QColor(255, 193, 7),
                'pending': QColor(108, 117, 125)
            }.get(status, QColor(108, 117, 125))
            status_item.setForeground(status_color)
            self.list_table.setItem(row, 4, status_item)

            # Duration
            duration_item = QTableWidgetItem(f"{video_data.get('duration', 0)}s")
            self.list_table.setItem(row, 5, duration_item)

            # Created
            created_at = video_data.get('created_at', '')
            if created_at:
                try:
                    date_obj = datetime.fromisoformat(created_at)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date_str = created_at
            else:
                date_str = 'Unknown'
            created_item = QTableWidgetItem(date_str)
            self.list_table.setItem(row, 6, created_item)

            # Set row height
            self.list_table.setRowHeight(row, 70)

    def switch_view_mode(self, mode: str):
        """Switch between grid and list view"""
        self.current_view_mode = mode

        if mode == 'grid':
            self.list_table.hide()
            self.grid_scroll.show()
        else:
            self.grid_scroll.hide()
            self.list_table.show()

        self.display_current_page()
        logger.info(f"Switched to {mode} view")

    def on_filter_changed(self):
        """Handle filter change"""
        # Update current filters
        self.current_filters['search'] = self.search_input.text()
        self.current_filters['date_from'] = self.date_from.date()
        self.current_filters['date_to'] = self.date_to.date()
        self.current_filters['model'] = self.model_filter.currentText()
        self.current_filters['status'] = self.status_filter.currentText()

        # Reload with new filters
        self.load_history()

    def on_sort_changed(self, index: int):
        """Handle sort change"""
        sort_map = {
            0: 'date_desc',
            1: 'date_asc',
            2: 'duration_desc',
            3: 'duration_asc',
            4: 'name_asc',
            5: 'name_desc'
        }
        self.current_filters['sort_by'] = sort_map.get(index, 'date_desc')
        self.load_history()

    def clear_filters(self):
        """Clear all filters"""
        self.search_input.clear()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        self.model_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)

        self.current_filters = {
            'search': '',
            'date_from': None,
            'date_to': None,
            'model': 'All',
            'status': 'All',
            'sort_by': 'date_desc'
        }

        self.load_history()
        logger.info("Filters cleared")

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
            self.update_pagination_ui()

    def next_page(self):
        """Go to next page"""
        max_page = (self.total_videos - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self.display_current_page()
            self.update_pagination_ui()

    def update_pagination_ui(self):
        """Update pagination button states and label"""
        max_page = max(0, (self.total_videos - 1) // self.page_size)
        current_page_display = self.current_page + 1
        total_pages_display = max_page + 1

        self.page_label.setText(f"Page {current_page_display} of {total_pages_display}")
        self.prev_page_btn.setEnabled(self.current_page > 0)
        self.next_page_btn.setEnabled(self.current_page < max_page)

    def update_results_count(self):
        """Update results count label"""
        video_text = "video" if self.total_videos == 1 else "videos"
        self.results_label.setText(f"{self.total_videos} {video_text}")

    def on_video_clicked(self, video_id: int):
        """Handle video card click"""
        if video_id in self.selected_video_ids:
            self.selected_video_ids.remove(video_id)
        else:
            self.selected_video_ids.add(video_id)
        logger.info(f"Video {video_id} selection toggled")

    def on_video_double_clicked(self, video_id: int):
        """Handle video card double click - open video"""
        logger.info(f"Opening video {video_id}")
        self.open_video(video_id)

    def on_table_double_click(self, index):
        """Handle table row double click"""
        row = index.row()
        id_item = self.list_table.item(row, 0)
        if id_item:
            video_id = id_item.data(Qt.ItemDataRole.UserRole)
            self.open_video(video_id)

    def show_context_menu(self, video_id: int, pos):
        """Show context menu for video card"""
        # Find video data
        video_data = None
        for video in self.filtered_videos:
            if video.get('id') == video_id:
                video_data = video
                break

        if not video_data:
            return

        menu = QMenu(self)

        # Open
        open_action = QAction("Open Video", self)
        open_action.triggered.connect(lambda: self.open_video(video_id))
        menu.addAction(open_action)

        # Open location
        open_location_action = QAction("Open File Location", self)
        open_location_action.triggered.connect(lambda: self.open_file_location(video_id))
        menu.addAction(open_location_action)

        menu.addSeparator()

        # Copy prompt
        copy_prompt_action = QAction("Copy Prompt", self)
        copy_prompt_action.triggered.connect(lambda: self.copy_prompt(video_id))
        menu.addAction(copy_prompt_action)

        # Export info
        export_info_action = QAction("Export Info", self)
        export_info_action.triggered.connect(lambda: self.export_video_info(video_id))
        menu.addAction(export_info_action)

        menu.addSeparator()

        # Regenerate
        regenerate_action = QAction("Regenerate Video", self)
        regenerate_action.triggered.connect(lambda: self.regenerate_video(video_id))
        menu.addAction(regenerate_action)

        menu.addSeparator()

        # Delete
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_video(video_id))
        menu.addAction(delete_action)

        menu.exec(pos)

    def show_table_context_menu(self, pos):
        """Show context menu for table view"""
        # Get selected rows
        selected_rows = self.list_table.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        id_item = self.list_table.item(row, 0)
        if not id_item:
            return

        video_id = id_item.data(Qt.ItemDataRole.UserRole)
        global_pos = self.list_table.viewport().mapToGlobal(pos)
        self.show_context_menu(video_id, global_pos)

    def open_video(self, video_id: int):
        """Open video file"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            QMessageBox.warning(self, "Error", "Video not found")
            return

        video_path = video_data.get('video_path')
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "Error", "Video file not found")
            return

        # Open with default application
        try:
            import platform
            if platform.system() == 'Windows':
                os.startfile(video_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{video_path}"')
            else:  # Linux
                os.system(f'xdg-open "{video_path}"')
            logger.info(f"Opened video: {video_path}")
        except Exception as e:
            logger.error(f"Failed to open video: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open video:\n{str(e)}")

    def open_file_location(self, video_id: int):
        """Open video file location in file explorer"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            return

        video_path = video_data.get('video_path')
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "Error", "Video file not found")
            return

        # Open folder and select file
        try:
            import platform
            folder = os.path.dirname(video_path)
            if platform.system() == 'Windows':
                os.system(f'explorer /select,"{video_path}"')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open -R "{video_path}"')
            else:  # Linux
                os.system(f'xdg-open "{folder}"')
            logger.info(f"Opened file location: {folder}")
        except Exception as e:
            logger.error(f"Failed to open file location: {e}")

    def copy_prompt(self, video_id: int):
        """Copy video prompt to clipboard"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            return

        prompt = video_data.get('prompt', '')
        if prompt:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(prompt)
            logger.info(f"Copied prompt to clipboard for video {video_id}")
            QMessageBox.information(self, "Success", "Prompt copied to clipboard!")

    def export_video_info(self, video_id: int):
        """Export video information to JSON file"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            return

        # Ask for save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Video Info",
            f"video_{video_id}_info.json",
            "JSON Files (*.json)"
        )

        if filename:
            try:
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(video_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Exported video info to {filename}")
                QMessageBox.information(self, "Success", f"Video info exported to:\n{filename}")
            except Exception as e:
                logger.error(f"Failed to export video info: {e}")
                QMessageBox.critical(self, "Error", f"Failed to export video info:\n{str(e)}")

    def regenerate_video(self, video_id: int):
        """Request video regeneration"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            return

        reply = QMessageBox.question(
            self,
            "Regenerate Video",
            f"Regenerate this video?\n\nPrompt: {video_data.get('prompt', 'N/A')[:100]}...",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info(f"Regenerating video {video_id}")
            self.video_regenerated.emit(video_data)

    def delete_video(self, video_id: int):
        """Delete a single video"""
        video_data = self.get_video_by_id(video_id)
        if not video_data:
            return

        reply = QMessageBox.question(
            self,
            "Delete Video",
            f"Are you sure you want to delete this video?\n\n{video_data.get('filename', 'Unknown')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete video file
                video_path = video_data.get('video_path')
                if video_path and os.path.exists(video_path):
                    os.remove(video_path)

                # Delete thumbnail
                thumbnail_path = video_data.get('thumbnail_path')
                if thumbnail_path and os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)

                # Delete from database
                if self.db_manager:
                    self.db_manager.delete_video(video_id)

                logger.info(f"Deleted video {video_id}")
                self.video_deleted.emit(video_id)
                self.refresh_history()
                QMessageBox.information(self, "Success", "Video deleted successfully!")

            except Exception as e:
                logger.error(f"Failed to delete video: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete video:\n{str(e)}")

    def bulk_delete(self, video_ids: List[int]):
        """Delete multiple videos"""
        if not video_ids:
            QMessageBox.warning(self, "Warning", "No videos selected")
            return

        reply = QMessageBox.question(
            self,
            "Bulk Delete",
            f"Are you sure you want to delete {len(video_ids)} videos?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            failed_count = 0

            for video_id in video_ids:
                try:
                    video_data = self.get_video_by_id(video_id)
                    if video_data:
                        # Delete video file
                        video_path = video_data.get('video_path')
                        if video_path and os.path.exists(video_path):
                            os.remove(video_path)

                        # Delete thumbnail
                        thumbnail_path = video_data.get('thumbnail_path')
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)

                        # Delete from database
                        if self.db_manager:
                            self.db_manager.delete_video(video_id)

                        success_count += 1
                        self.video_deleted.emit(video_id)
                except Exception as e:
                    logger.error(f"Failed to delete video {video_id}: {e}")
                    failed_count += 1

            self.refresh_history()
            self.selected_video_ids.clear()

            msg = f"Deleted {success_count} videos"
            if failed_count > 0:
                msg += f"\nFailed to delete {failed_count} videos"

            QMessageBox.information(self, "Bulk Delete Complete", msg)
            logger.info(f"Bulk delete completed: {success_count} success, {failed_count} failed")

    def select_all_videos(self):
        """Select all videos on current page"""
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_videos = self.filtered_videos[start_idx:end_idx]

        for video in page_videos:
            self.selected_video_ids.add(video.get('id'))

        logger.info(f"Selected {len(page_videos)} videos")
        QMessageBox.information(self, "Info", f"Selected {len(page_videos)} videos on current page")

    def deselect_all_videos(self):
        """Deselect all videos"""
        count = len(self.selected_video_ids)
        self.selected_video_ids.clear()
        logger.info(f"Deselected {count} videos")

    def bulk_delete_videos(self):
        """Delete all selected videos"""
        if not self.selected_video_ids:
            QMessageBox.warning(self, "Warning", "No videos selected")
            return

        self.bulk_delete(list(self.selected_video_ids))

    def refresh_history(self):
        """Refresh video history"""
        logger.info("Refreshing history...")
        self.load_history()
        QMessageBox.information(self, "Success", "History refreshed!")

    def update_storage_info(self):
        """Update storage information"""
        try:
            total_size = 0
            output_dir = Path("outputs")

            if output_dir.exists():
                for file in output_dir.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size

            # Convert to human readable
            size_mb = total_size / (1024 * 1024)
            size_gb = size_mb / 1024

            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            else:
                size_str = f"{size_mb:.2f} MB"

            self.storage_label.setText(f"Storage: {size_str}")
            logger.info(f"Storage: {size_str}")

        except Exception as e:
            logger.error(f"Failed to calculate storage: {e}")
            self.storage_label.setText("Storage: Unknown")

    def clear_cache(self):
        """Clear thumbnail cache"""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "This will delete all cached thumbnails.\nVideos will not be affected.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                cache_dir = Path("outputs/thumbnails")
                if cache_dir.exists():
                    deleted_count = 0
                    for file in cache_dir.rglob("*.jpg"):
                        file.unlink()
                        deleted_count += 1

                    logger.info(f"Cleared {deleted_count} thumbnails from cache")
                    QMessageBox.information(self, "Success", f"Cleared {deleted_count} thumbnails from cache!")
                else:
                    QMessageBox.information(self, "Info", "No cache to clear")
            except Exception as e:
                logger.error(f"Failed to clear cache: {e}")
                QMessageBox.critical(self, "Error", f"Failed to clear cache:\n{str(e)}")

    def get_video_by_id(self, video_id: int) -> Optional[Dict[str, Any]]:
        """Get video data by ID"""
        for video in self.all_videos:
            if video.get('id') == video_id:
                return video
        return None

    def generate_mock_data(self) -> List[Dict[str, Any]]:
        """Generate mock video data for testing"""
        mock_videos = []

        prompts = [
            "A serene sunset over mountains",
            "Bustling city street at night",
            "Ocean waves crashing on beach",
            "Time-lapse of clouds moving",
            "Forest path with sunlight filtering through trees",
            "Modern architecture building exterior",
            "Abstract colorful patterns",
            "Wildlife in natural habitat",
            "Underwater coral reef scene",
            "Space nebula with stars"
        ]

        statuses = ['completed', 'completed', 'completed', 'failed', 'processing']
        models = ['veo-2.0', 'veo-1.0']

        for i in range(50):
            video_id = i + 1
            status = statuses[i % len(statuses)]

            mock_videos.append({
                'id': video_id,
                'prompt': prompts[i % len(prompts)],
                'model': models[i % len(models)],
                'status': status,
                'duration': 5 + (i % 3) * 3,
                'filename': f"video_{video_id}.mp4",
                'video_path': f"outputs/video_{video_id}.mp4" if status == 'completed' else None,
                'thumbnail_path': f"outputs/thumbnails/thumb_{video_id}.jpg" if status == 'completed' else None,
                'created_at': (datetime.now() - timedelta(days=i % 30, hours=i % 24)).isoformat(),
                'aspect_ratio': '16:9',
                'resolution': '1080p'
            })

        return mock_videos
