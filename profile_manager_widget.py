"""
Profile Manager Widget - UI for VTS settings profiles
"""

import logging
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit, QTextEdit,
    QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from vts_profile_manager import VTSProfileManager, ProfileInfo, ProfileCategory
from vts_discovery import get_vts_discovery

logger = logging.getLogger(__name__)


class CreateProfileDialog(QDialog):
    """Dialog for creating a new profile."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.profile_name = ""
        self.profile_category = ProfileCategory.COMPLETE
        self.profile_description = ""
        
        self.setup_ui()
        self.apply_dark_theme()
        self.setWindowTitle("Create Profile")
        self.resize(500, 350)
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<b>Create New Profile</b>")
        header.setStyleSheet("color: #ffffff; font-size: 14px; background-color: transparent;")
        layout.addWidget(header)
        
        # Name
        name_label = QLabel("Profile Name:")
        name_label.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter profile name...")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.name_edit)
        
        # Category
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("Complete (All Settings)", ProfileCategory.COMPLETE)
        self.category_combo.addItem("Tracking Only", ProfileCategory.TRACKING)
        self.category_combo.addItem("API Settings Only", ProfileCategory.API)
        self.category_combo.addItem("UI Settings Only", ProfileCategory.UI)
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #007acc;
            }
        """)
        layout.addWidget(self.category_combo)
        
        # Description
        desc_label = QLabel("Description (optional):")
        desc_label.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(desc_label)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter description...")
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Profile")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        create_btn.clicked.connect(self.accept_create)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
    
    def apply_dark_theme(self):
        """Apply dark theme."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
            }
        """)
    
    def accept_create(self):
        """Accept and validate."""
        name = self.name_edit.text().strip()
        if not name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Invalid Name")
            msg.setText("Please enter a profile name.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; border: none; padding: 6px 20px; }
            """)
            msg.exec()
            return
        
        self.profile_name = name
        self.profile_category = self.category_combo.currentData()
        self.profile_description = self.desc_edit.toPlainText().strip()
        self.accept()


class ProfileManagerWidget(QWidget):
    """Widget for managing VTS settings profiles."""
    
    profile_loaded = pyqtSignal(str)  # Emits profile name when loaded
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.manager = VTSProfileManager()
        self.discovery = get_vts_discovery()
        self.profiles: List[ProfileInfo] = []
        
        self.setup_ui()
        self.refresh_profiles()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        
        header_label = QLabel("<b>VTS Settings Profiles</b>")
        header_label.setStyleSheet("color: #ffffff; font-size: 14px; background-color: transparent;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refresh profile list")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_profiles)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #007acc;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
        self.profile_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.profile_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("Create Profile")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        self.create_btn.clicked.connect(self.create_profile)
        button_layout.addWidget(self.create_btn)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.setEnabled(False)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.load_btn.clicked.connect(self.load_profile)
        button_layout.addWidget(self.load_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setEnabled(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.export_btn.clicked.connect(self.export_profile)
        button_layout.addWidget(self.export_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_profile)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        
        # Import button
        import_btn = QPushButton("Import Profile...")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 6px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        import_btn.clicked.connect(self.import_profile)
        layout.addWidget(import_btn)
    
    def refresh_profiles(self):
        """Refresh the profile list."""
        self.profile_list.clear()
        self.profiles = self.manager.list_profiles()
        
        for profile in self.profiles:
            item = QListWidgetItem()
            item.setText(f"{profile.name}\n{profile.category.value} | {profile.created_date.strftime('%Y-%m-%d %H:%M')}")
            item.setData(Qt.ItemDataRole.UserRole, profile.name)
            self.profile_list.addItem(item)
        
        logger.info(f"Refreshed profile list: {len(self.profiles)} profiles")
    
    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = len(self.profile_list.selectedItems()) > 0
        self.load_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def create_profile(self):
        """Create a new profile."""
        # Get current VTS config
        vts_config_path = self.discovery.get_vts_config_path()
        if not vts_config_path:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("VTS Not Found")
            msg.setText("VTube Studio configuration not found.\nPlease ensure VTS is installed.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
            return
        
        # Show create dialog
        dialog = CreateProfileDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Load current VTS config
        import json
        try:
            with open(vts_config_path, 'r', encoding='utf-8') as f:
                vts_config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load VTS config: {e}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to load VTS configuration:\n{e}")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
            return
        
        # Filter by category if needed
        if dialog.profile_category != ProfileCategory.COMPLETE:
            vts_config = self.manager.filter_settings_by_category(
                vts_config,
                dialog.profile_category
            )
        
        # Save profile
        success = self.manager.save_profile(
            dialog.profile_name,
            vts_config,
            dialog.profile_category,
            dialog.profile_description
        )
        
        if success:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Profile '{dialog.profile_name}' created successfully!")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #007acc; color: #ffffff; }
            """)
            msg.exec()
            self.refresh_profiles()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Failed to create profile. Check logs for details.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
    
    def load_profile(self):
        """Load selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return
        
        profile_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Load")
        msg.setText(f"Load profile '{profile_name}'?\n\nThis will change your current VTS settings.\nMake sure VTS is closed before proceeding.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #3d3d3d; color: #ffffff; }
        """)
        
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return
        
        # TODO: Implement actual profile loading to VTS
        info_msg = QMessageBox(self)
        info_msg.setIcon(QMessageBox.Icon.Information)
        info_msg.setWindowTitle("Feature In Progress")
        info_msg.setText("Profile loading will be implemented in the next update.\n\nFor now, profiles are saved and can be exported.")
        info_msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #007acc; color: #ffffff; }
        """)
        info_msg.exec()
    
    def export_profile(self):
        """Export selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return
        
        profile_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Profile",
            f"{profile_name}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            success = self.manager.export_profile(profile_name, Path(file_path))
            if success:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Profile exported to:\n{file_path}")
                msg.setStyleSheet("""
                    QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                    QLabel { color: #ffffff; }
                    QPushButton { background-color: #007acc; color: #ffffff; }
                """)
                msg.exec()
    
    def delete_profile(self):
        """Delete selected profile."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            return
        
        profile_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Confirm Delete")
        msg.setText(f"Delete profile '{profile_name}'?\n\nThis action cannot be undone.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #3d3d3d; color: #ffffff; }
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            success = self.manager.delete_profile(profile_name)
            if success:
                self.refresh_profiles()
    
    def import_profile(self):
        """Import a profile."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Profile",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        
        if file_path:
            profile_name = self.manager.import_profile(Path(file_path))
            if profile_name:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Profile '{profile_name}' imported successfully!")
                msg.setStyleSheet("""
                    QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                    QLabel { color: #ffffff; }
                    QPushButton { background-color: #007acc; color: #ffffff; }
                """)
                msg.exec()
                self.refresh_profiles()
