"""
Transfer Dialog - Detailed settings transfer configuration
"""

import logging
from typing import List, Set, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QTreeWidget, QTreeWidgetItem, QGroupBox, QTabWidget,
    QWidget, QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from vts_discovery import ModelInfo
from vts_file_parser import VTSFileParser, HotkeyInfo, ParameterInfo
from model_settings_manager import TransferSettings

logger = logging.getLogger(__name__)


class TransferDialog(QDialog):
    """Dialog for configuring detailed transfer settings."""
    
    def __init__(self, source_model: ModelInfo, target_model: ModelInfo, parent=None):
        super().__init__(parent)
        
        self.source_model = source_model
        self.target_model = target_model
        
        # Load model data
        self.source_data = VTSFileParser.load_vtube_json(source_model.vtube_json_path)
        self.target_data = VTSFileParser.load_vtube_json(target_model.vtube_json_path)
        
        if not self.source_data or not self.target_data:
            raise ValueError("Failed to load model data")
        
        # Parse hotkeys and parameters
        self.source_hotkeys = VTSFileParser.parse_hotkeys(self.source_data)
        self.source_parameters = VTSFileParser.parse_parameters(self.source_data)
        
        # Selected items
        self.selected_hotkey_ids: Set[str] = set()
        self.selected_parameter_names: Set[str] = set()
        
        # Transfer settings
        self.transfer_settings: Optional[TransferSettings] = None
        
        self.setup_ui()
        self.apply_dark_theme()
        self.setWindowTitle(f"Transfer Settings: {source_model.name} → {target_model.name}")
        self.resize(800, 600)
    
    def apply_dark_theme(self):
        """Apply dark theme to dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QCheckBox {
                color: #ffffff;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
            }
        """)
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tabs for different transfer types
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
        """)
        
        # Hotkeys tab
        hotkeys_tab = self.create_hotkeys_tab()
        tabs.addTab(hotkeys_tab, f"Hotkeys ({len(self.source_hotkeys)})")
        
        # Parameters tab
        parameters_tab = self.create_parameters_tab()
        tabs.addTab(parameters_tab, f"Parameters ({len(self.source_parameters)})")
        
        # Options tab
        options_tab = self.create_options_tab()
        tabs.addTab(options_tab, "Options")
        
        layout.addWidget(tabs, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview Changes")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        self.preview_btn.clicked.connect(self.show_preview)
        button_layout.addWidget(self.preview_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.transfer_btn = QPushButton("Transfer →")
        self.transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self.transfer_btn.clicked.connect(self.accept_transfer)
        button_layout.addWidget(self.transfer_btn)
        
        layout.addLayout(button_layout)
    
    def create_header(self) -> QWidget:
        """Create header with model info."""
        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d; border-radius: 5px; padding: 10px;")
        layout = QVBoxLayout(header)
        
        title = QLabel(f"<b>Transfer Settings</b>")
        title.setStyleSheet("color: #ffffff; font-size: 16px; background-color: transparent;")
        layout.addWidget(title)
        
        info = QLabel(
            f"From: <b>{self.source_model.name}</b><br>"
            f"To: <b>{self.target_model.name}</b>"
        )
        info.setStyleSheet("color: #cccccc; background-color: transparent;")
        layout.addWidget(info)
        
        return header
    
    def create_hotkeys_tab(self) -> QWidget:
        """Create hotkeys selection tab."""
        tab = QWidget()
        tab.setStyleSheet("background-color: #252525;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Bulk select
        bulk_layout = QHBoxLayout()
        
        self.select_all_hotkeys = QCheckBox("Select All")
        self.select_all_hotkeys.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.select_all_hotkeys.stateChanged.connect(self.on_select_all_hotkeys)
        bulk_layout.addWidget(self.select_all_hotkeys)
        
        bulk_layout.addStretch()
        
        count_label = QLabel(f"Total: {len(self.source_hotkeys)} hotkeys")
        count_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        bulk_layout.addWidget(count_label)
        
        layout.addLayout(bulk_layout)
        
        # Tree widget
        self.hotkeys_tree = QTreeWidget()
        self.hotkeys_tree.setHeaderLabels(["  Name", "Keybind", "Action", "File"])
        self.hotkeys_tree.setIndentation(0)
        self.hotkeys_tree.setRootIsDecorated(False)
        self.hotkeys_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::item {
                padding: 8px 5px;
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d2d2d;
            }
            QTreeWidget::indicator {
                width: 18px;
                height: 18px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHZpZXdCb3g9IjAgMCAxOCAxOCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNNiAxMUw0IDlsLTEgMSAzIDMgNy03LTEtMXoiIGZpbGw9IiNmZmYiLz4KPC9zdmc+);
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px 5px;
            }
        """)
        
        # Populate hotkeys
        for hotkey in self.source_hotkeys:
            item = QTreeWidgetItem([
                hotkey.name,
                hotkey.get_keybind_string(),
                hotkey.action,
                hotkey.file
            ])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, hotkey.hotkey_id)
            self.hotkeys_tree.addTopLevelItem(item)
        
        # Set column widths manually to ensure proper spacing
        self.hotkeys_tree.setColumnWidth(0, 300)  # Name column (wider for checkbox + text)
        self.hotkeys_tree.setColumnWidth(1, 150)  # Keybind column
        self.hotkeys_tree.setColumnWidth(2, 150)  # Action column
        self.hotkeys_tree.setColumnWidth(3, 200)  # File column
        
        self.hotkeys_tree.itemChanged.connect(self.on_hotkey_item_changed)
        layout.addWidget(self.hotkeys_tree)
        
        return tab
    
    def create_parameters_tab(self) -> QWidget:
        """Create parameters selection tab."""
        tab = QWidget()
        tab.setStyleSheet("background-color: #252525;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Bulk select
        bulk_layout = QHBoxLayout()
        
        self.select_all_parameters = QCheckBox("Select All")
        self.select_all_parameters.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.select_all_parameters.stateChanged.connect(self.on_select_all_parameters)
        bulk_layout.addWidget(self.select_all_parameters)
        
        bulk_layout.addStretch()
        
        count_label = QLabel(f"Total: {len(self.source_parameters)} parameters")
        count_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        bulk_layout.addWidget(count_label)
        
        layout.addLayout(bulk_layout)
        
        # Tree widget
        self.parameters_tree = QTreeWidget()
        self.parameters_tree.setHeaderLabels(["  Name", "Input", "Output", "Range"])
        self.parameters_tree.setIndentation(0)
        self.parameters_tree.setRootIsDecorated(False)
        self.parameters_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::item {
                padding: 8px 5px;
                background-color: transparent;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d2d2d;
            }
            QTreeWidget::indicator {
                width: 18px;
                height: 18px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
            }
            QTreeWidget::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHZpZXdCb3g9IjAgMCAxOCAxOCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNNiAxMUw0IDlsLTEgMSAzIDMgNy03LTEtMXoiIGZpbGw9IiNmZmYiLz4KPC9zdmc+);
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px 5px;
            }
        """)
        
        # Populate parameters
        for param in self.source_parameters:
            range_str = f"{param.output_range[0]:.1f} to {param.output_range[1]:.1f}"
            item = QTreeWidgetItem([
                param.name,
                param.input_param,
                param.output_param,
                range_str
            ])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, param.name)
            self.parameters_tree.addTopLevelItem(item)
        
        # Set column widths manually to ensure proper spacing
        self.parameters_tree.setColumnWidth(0, 300)  # Name column (wider for checkbox + text)
        self.parameters_tree.setColumnWidth(1, 150)  # Input column
        self.parameters_tree.setColumnWidth(2, 150)  # Output column
        self.parameters_tree.setColumnWidth(3, 120)  # Range column
        
        self.parameters_tree.itemChanged.connect(self.on_parameter_item_changed)
        layout.addWidget(self.parameters_tree)
        
        return tab
    
    def create_options_tab(self) -> QWidget:
        """Create options tab."""
        tab = QWidget()
        tab.setStyleSheet("background-color: #252525;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Options group
        options_group = QGroupBox("Transfer Options")
        options_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        options_layout = QVBoxLayout(options_group)
        
        self.generate_ids_check = QCheckBox("Generate new hotkey IDs (recommended)")
        self.generate_ids_check.setChecked(True)
        self.generate_ids_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        options_layout.addWidget(self.generate_ids_check)
        
        self.copy_files_check = QCheckBox("Copy expression files (.exp3.json, .motion3.json)")
        self.copy_files_check.setChecked(True)
        self.copy_files_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        options_layout.addWidget(self.copy_files_check)
        
        self.create_backup_check = QCheckBox("Create backup before transfer (recommended)")
        self.create_backup_check.setChecked(True)
        self.create_backup_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        options_layout.addWidget(self.create_backup_check)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        return tab
    
    def on_select_all_hotkeys(self, state):
        """Handle select all hotkeys."""
        check_state = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        
        # Block signals to avoid triggering itemChanged for each item
        self.hotkeys_tree.blockSignals(True)
        for i in range(self.hotkeys_tree.topLevelItemCount()):
            item = self.hotkeys_tree.topLevelItem(i)
            item.setCheckState(0, check_state)
            
            # Update selection set
            hotkey_id = item.data(0, Qt.ItemDataRole.UserRole)
            if check_state == Qt.CheckState.Checked:
                self.selected_hotkey_ids.add(hotkey_id)
            else:
                self.selected_hotkey_ids.discard(hotkey_id)
        
        self.hotkeys_tree.blockSignals(False)
    
    def on_select_all_parameters(self, state):
        """Handle select all parameters."""
        check_state = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        
        # Block signals to avoid triggering itemChanged for each item
        self.parameters_tree.blockSignals(True)
        for i in range(self.parameters_tree.topLevelItemCount()):
            item = self.parameters_tree.topLevelItem(i)
            item.setCheckState(0, check_state)
            
            # Update selection set
            param_name = item.data(0, Qt.ItemDataRole.UserRole)
            if check_state == Qt.CheckState.Checked:
                self.selected_parameter_names.add(param_name)
            else:
                self.selected_parameter_names.discard(param_name)
        
        self.parameters_tree.blockSignals(False)
    
    def on_hotkey_item_changed(self, item, column):
        """Handle hotkey item check state change."""
        if column == 0:
            hotkey_id = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(0) == Qt.CheckState.Checked:
                self.selected_hotkey_ids.add(hotkey_id)
            else:
                self.selected_hotkey_ids.discard(hotkey_id)
    
    def on_parameter_item_changed(self, item, column):
        """Handle parameter item check state change."""
        if column == 0:
            param_name = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(0) == Qt.CheckState.Checked:
                self.selected_parameter_names.add(param_name)
            else:
                self.selected_parameter_names.discard(param_name)
    
    def show_preview(self):
        """Show transfer preview dialog."""
        from preview_dialog import PreviewDialog
        
        settings = self.build_transfer_settings()
        preview = PreviewDialog(
            self.source_model,
            self.target_model,
            settings,
            self
        )
        preview.exec()
    
    def build_transfer_settings(self) -> TransferSettings:
        """Build transfer settings from current selections."""
        return TransferSettings(
            transfer_all_hotkeys=False,
            selected_hotkey_ids=list(self.selected_hotkey_ids),
            transfer_all_parameters=False,
            selected_parameter_names=list(self.selected_parameter_names),
            generate_new_ids=self.generate_ids_check.isChecked(),
            copy_expression_files=self.copy_files_check.isChecked(),
            create_backup=self.create_backup_check.isChecked(),
            dry_run=False
        )
    
    def accept_transfer(self):
        """Accept and start transfer."""
        # Validate selections
        if not self.selected_hotkey_ids and not self.selected_parameter_names:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("No Selection")
            msg.setText("Please select at least one hotkey or parameter to transfer.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: none;
                    padding: 6px 20px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
            """)
            msg.exec()
            return
        
        # Build settings
        self.transfer_settings = self.build_transfer_settings()
        self.accept()
    
    def get_transfer_settings(self) -> Optional[TransferSettings]:
        """Get the configured transfer settings."""
        return self.transfer_settings
