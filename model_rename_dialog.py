"""
Model Rename Dialog - Rename or duplicate VTS models properly
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class ModelRenameDialog(QDialog):
    """Dialog for renaming/duplicating models."""
    
    def __init__(self, current_name: str, parent=None):
        super().__init__(parent)
        
        self.current_name = current_name
        self.new_name = ""
        self.create_new_id = False
        
        self.setup_ui()
        self.apply_dark_theme()
        self.setWindowTitle("Rename Model")
        self.resize(500, 300)
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<b>Rename Model</b>")
        header.setStyleSheet("color: #ffffff; font-size: 14px; background-color: transparent;")
        layout.addWidget(header)
        
        # Info
        info = QLabel(
            "This will rename the model folder, .vtube.json file, and update the Name field inside the config.\n"
            "VTube Studio must be closed before renaming."
        )
        info.setStyleSheet("color: #cccccc; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Current name
        current_group = QGroupBox("Current Name")
        current_group.setStyleSheet("""
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
        current_layout = QVBoxLayout(current_group)
        
        current_label = QLabel(self.current_name)
        current_label.setStyleSheet("color: #ffffff; font-weight: bold; background-color: transparent;")
        current_layout.addWidget(current_label)
        
        layout.addWidget(current_group)
        
        # New name
        new_group = QGroupBox("New Name")
        new_group.setStyleSheet("""
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
        new_layout = QVBoxLayout(new_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.current_name)
        self.name_edit.setPlaceholderText("Enter new model name...")
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 3px;
                font-size: 12pt;
            }
        """)
        self.name_edit.selectAll()
        new_layout.addWidget(self.name_edit)
        
        layout.addWidget(new_group)
        
        # Options
        options_group = QGroupBox("Options")
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
        
        self.new_id_check = QCheckBox("Create new Model ID (duplicate as separate model)")
        self.new_id_check.setChecked(True)
        self.new_id_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        self.new_id_check.setToolTip(
            "If checked, generates a new unique ModelID.\n"
            "VTube Studio will treat this as a completely new model.\n"
            "All hotkeys and settings will be independent.\n\n"
            "If unchecked, keeps the same ModelID (not recommended if original model still exists)."
        )
        options_layout.addWidget(self.new_id_check)
        
        id_info = QLabel(
            "ℹ Recommended: Keep this checked if you duplicated the model.\n"
            "This ensures VTS treats it as a separate model with independent settings."
        )
        id_info.setStyleSheet("color: #888888; font-size: 9pt; background-color: transparent;")
        id_info.setWordWrap(True)
        options_layout.addWidget(id_info)
        
        layout.addWidget(options_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
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
        
        rename_btn = QPushButton("Rename Model")
        rename_btn.setStyleSheet("""
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
        rename_btn.clicked.connect(self.accept_rename)
        button_layout.addWidget(rename_btn)
        
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
    
    def accept_rename(self):
        """Accept and validate."""
        new_name = self.name_edit.text().strip()
        
        if not new_name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Invalid Name")
            msg.setText("Please enter a new model name.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
            return
        
        if new_name == self.current_name:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Same Name")
            msg.setText("The new name is the same as the current name.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
            return
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in new_name for char in invalid_chars):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Invalid Characters")
            msg.setText(f"Model name cannot contain: {' '.join(invalid_chars)}")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
            return
        
        self.new_name = new_name
        self.create_new_id = self.new_id_check.isChecked()
        self.accept()
