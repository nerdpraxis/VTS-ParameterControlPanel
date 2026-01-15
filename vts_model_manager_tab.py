"""
VTS Model Manager Tab - Main UI for model settings management
"""

import logging
from pathlib import Path
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QComboBox, QScrollArea, QMessageBox, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from vts_discovery import VTSDiscovery, ModelInfo, get_vts_discovery
from vts_file_parser import VTSFileParser, HotkeyInfo, ParameterInfo
from model_settings_manager import ModelSettingsManager, TransferSettings
from transfer_dialog import TransferDialog
from profile_manager_widget import ProfileManagerWidget
from model_rename_dialog import ModelRenameDialog
from model_renamer import ModelRenamer, RenameResult

logger = logging.getLogger(__name__)


def create_dark_messagebox(parent, icon, title, text, buttons=QMessageBox.StandardButton.Ok):
    """Create a dark-themed message box."""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    
    # Apply dark theme
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
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
        QPushButton:default {
            background-color: #007acc;
        }
        QPushButton:default:hover {
            background-color: #0098ff;
        }
    """)
    
    return msg


class ModelSelectorWidget(QWidget):
    """Widget for selecting a VTS model."""
    
    def __init__(self, title: str = "Select Model", parent=None):
        super().__init__(parent)
        self.models: List[ModelInfo] = []
        self.selected_model: Optional[ModelInfo] = None
        self.title = title
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"<b>{self.title}</b>")
        title_label.setStyleSheet("color: #ffffff; font-size: 14px; background-color: transparent;")
        layout.addWidget(title_label)
        
        # Dropdown with rename button
        combo_layout = QHBoxLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #007acc;
            }
        """)
        self.model_combo.currentIndexChanged.connect(self.on_model_selected)
        combo_layout.addWidget(self.model_combo, 1)
        
        # Rename button
        self.rename_btn = QPushButton("✏ Rename")
        self.rename_btn.setToolTip("Rename this model")
        self.rename_btn.setEnabled(False)
        self.rename_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: none;
                padding: 5px 10px;
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
        self.rename_btn.clicked.connect(self.rename_model)
        combo_layout.addWidget(self.rename_btn)
        
        layout.addLayout(combo_layout)
        
        # Info area
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: transparent;")
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 10, 0, 0)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(80, 80)
        self.thumbnail_label.setStyleSheet("border: 1px solid #3d3d3d; background-color: #1e1e1e; color: #666666;")
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.thumbnail_label)
        
        # Model info
        self.info_label = QLabel("No model selected")
        self.info_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(self.info_label, 1)
        
        layout.addWidget(info_widget)
    
    def load_models(self, models: List[ModelInfo]):
        """Load models into the dropdown."""
        self.models = models
        self.model_combo.clear()
        
        for model in models:
            folder_name = model.folder_path.name if model.folder_path else "Unknown"
            display_name = f"{model.name} [{folder_name}]"
            self.model_combo.addItem(display_name)
        
        if models:
            self.on_model_selected(0)
    
    def on_model_selected(self, index: int):
        """Handle model selection."""
        if 0 <= index < len(self.models):
            self.selected_model = self.models[index]
            self.update_info_display()
            self.rename_btn.setEnabled(True)
        else:
            self.selected_model = None
            self.rename_btn.setEnabled(False)
    
    def update_info_display(self):
        """Update the info display for selected model."""
        if not self.selected_model:
            self.info_label.setText("No model selected")
            self.thumbnail_label.clear()
            return
        
        model = self.selected_model
        
        # Update thumbnail
        if model.thumbnail:
            scaled_pixmap = model.thumbnail.scaled(
                80, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
        else:
            self.thumbnail_label.setText("No\nIcon")
        
        # Update info text
        info_text = f"""
<b>Name:</b> {model.name}<br>
<b>ID:</b> {model.model_id[:16]}...<br>
<b>Hotkeys:</b> {model.hotkey_count}<br>
<b>Parameters:</b> {model.parameter_count}<br>
<b>Expressions:</b> {model.expression_count}
        """.strip()
        
        self.info_label.setText(info_text)
    
    def get_selected_model(self) -> Optional[ModelInfo]:
        """Get the currently selected model."""
        return self.selected_model
    
    def rename_model(self):
        """Rename the currently selected model."""
        if not self.selected_model:
            return
        
        # Emit signal to parent to handle rename
        # Or call parent's rename method directly
        parent = self.parent()
        while parent:
            if isinstance(parent, VTSModelManagerTab):
                parent.rename_selected_model(self.selected_model)
                break
            parent = parent.parent()


class VTSModelManagerTab(QWidget):
    """Main tab for VTS model management."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.discovery = get_vts_discovery()
        self.manager = ModelSettingsManager()
        self.renamer = ModelRenamer()
        
        self.models: List[ModelInfo] = []
        
        self.setup_ui()
        self.discover_vts()
    
    def setup_ui(self):
        """Setup the UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252525;
            }
            QWidget {
                background-color: #252525;
            }
        """)
        
        # Content widget
        content = QWidget()
        content.setStyleSheet("background-color: #252525;")
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Discovery section
        discovery_group = self.create_discovery_section()
        layout.addWidget(discovery_group)
        
        # Model transfer section
        transfer_group = self.create_transfer_section()
        layout.addWidget(transfer_group)
        
        # Profile manager section
        profile_group = self.create_profile_section()
        layout.addWidget(profile_group)
        
        # Spacer
        layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def create_discovery_section(self) -> QGroupBox:
        """Create the VTS discovery section."""
        group = QGroupBox("VTube Studio Installation")
        group.setStyleSheet("""
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
        
        layout = QVBoxLayout(group)
        
        # Status label
        self.status_label = QLabel("Searching for VTube Studio...")
        self.status_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.status_label)
        
        # Manual path button
        btn_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse for VTS Installation...")
        self.browse_btn.setStyleSheet("""
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
        """)
        self.browse_btn.clicked.connect(self.browse_for_vts)
        btn_layout.addWidget(self.browse_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return group
    
    def create_transfer_section(self) -> QGroupBox:
        """Create the model transfer section."""
        group = QGroupBox("Model Settings Transfer")
        group.setStyleSheet("""
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
        
        layout = QVBoxLayout(group)
        
        # Source model selector
        self.source_selector = ModelSelectorWidget("Source Model (copy from)")
        layout.addWidget(self.source_selector)
        
        # Target model selector
        self.target_selector = ModelSelectorWidget("Target Model (copy to)")
        layout.addWidget(self.target_selector)
        
        # Transfer button
        btn_layout = QHBoxLayout()
        self.transfer_btn = QPushButton("Transfer Settings →")
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
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #666666;
            }
        """)
        self.transfer_btn.clicked.connect(self.start_transfer)
        self.transfer_btn.setEnabled(False)
        btn_layout.addWidget(self.transfer_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return group
    
    def create_profile_section(self) -> QGroupBox:
        """Create the profile manager section."""
        group = QGroupBox("VTS Settings Profiles")
        group.setStyleSheet("""
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
        
        layout = QVBoxLayout(group)
        
        # Info label
        info_label = QLabel(
            "Save and load different VTube Studio global settings configurations.\n"
            "Useful for switching between streaming, recording, or testing setups."
        )
        info_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Profile manager widget
        self.profile_manager = ProfileManagerWidget()
        layout.addWidget(self.profile_manager)
        
        return group
    
    def discover_vts(self):
        """Discover VTS installation and models."""
        logger.info("=" * 60)
        logger.info("Starting VTS discovery...")
        logger.info("=" * 60)
        
        # Find VTS installation
        if self.discovery.find_vts_installation():
            logger.info(f"✓ VTS installation found at: {self.discovery.vts_root}")
            logger.info(f"  Models path: {self.discovery.models_path}")
            
            self.status_label.setText(
                f"✓ Found VTube Studio at: {self.discovery.vts_root}"
            )
            self.status_label.setStyleSheet("color: #00ff00; background-color: transparent;")
            
            # Load models
            logger.info("Loading models...")
            self.models = self.discovery.get_models_list()
            
            if self.models:
                logger.info(f"✓ Successfully loaded {len(self.models)} models:")
                for model in self.models:
                    logger.info(f"  • {model.name} (ID: {model.model_id[:8]}..., {model.hotkey_count} hotkeys)")
                
                self.source_selector.load_models(self.models)
                self.target_selector.load_models(self.models)
                self.transfer_btn.setEnabled(True)
                
                self.status_label.setText(
                    f"✓ Found VTube Studio at: {self.discovery.vts_root} ({len(self.models)} models loaded)"
                )
            else:
                logger.warning("⚠ No models found in VTube Studio installation")
                logger.warning(f"  Checked path: {self.discovery.models_path}")
                self.status_label.setText(
                    f"⚠ Found VTube Studio but no models found. Check logs for details."
                )
                self.status_label.setStyleSheet("color: #ffaa00; background-color: transparent;")
        else:
            logger.error("✗ VTube Studio installation not found")
            self.status_label.setText(
                "✗ VTube Studio not found. Please browse manually."
            )
            self.status_label.setStyleSheet("color: #ff0000; background-color: transparent;")
        
        logger.info("=" * 60)
    
    def browse_for_vts(self):
        """Browse for VTS installation manually."""
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setWindowTitle("Select VTube Studio Installation Folder")
        dialog.setDirectory(str(Path.home()))
        
        # Apply dark theme
        dialog.setStyleSheet("""
            QFileDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)
        
        if not dialog.exec():
            return
        
        folders = dialog.selectedFiles()
        if not folders:
            return
        
        folder = folders[0]
        
        if folder:
            path = Path(folder)
            if self.discovery.find_vts_installation(path):
                self.status_label.setText(f"✓ Found VTube Studio at: {path}")
                self.status_label.setStyleSheet("color: #00ff00;")
                
                # Reload models
                self.models = self.discovery.get_models_list()
                self.source_selector.load_models(self.models)
                self.target_selector.load_models(self.models)
                self.transfer_btn.setEnabled(True)
            else:
                msg = create_dark_messagebox(
                    self,
                    QMessageBox.Icon.Warning,
                    "Invalid Path",
                    "The selected folder does not appear to be a valid VTube Studio installation.\n\n"
                    "Please select the folder containing 'VTube Studio_Data'."
                )
                msg.exec()
    
    def start_transfer(self):
        """Start the transfer process."""
        source_model = self.source_selector.get_selected_model()
        target_model = self.target_selector.get_selected_model()
        
        if not source_model or not target_model:
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Warning,
                "No Selection",
                "Please select both source and target models."
            )
            msg.exec()
            return
        
        if source_model.model_id == target_model.model_id:
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Warning,
                "Same Model",
                "Source and target models must be different."
            )
            msg.exec()
            return
        
        # Show detailed transfer dialog
        try:
            dialog = TransferDialog(source_model, target_model, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings = dialog.get_transfer_settings()
                if settings:
                    self.execute_transfer_with_settings(source_model, target_model, settings)
        except Exception as e:
            logger.exception("Error opening transfer dialog:")
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Critical,
                "Error",
                f"Failed to open transfer dialog:\n{e}"
            )
            msg.exec()
    
    def execute_transfer_with_settings(
        self,
        source_model: ModelInfo,
        target_model: ModelInfo,
        settings: TransferSettings
    ):
        """Execute the transfer operation with custom settings."""
        try:
            # Execute transfer
            logger.info("Starting transfer operation...")
            result = self.manager.execute_transfer(
                source_model.vtube_json_path,
                target_model.vtube_json_path,
                settings
            )
            
            # Show detailed result dialog
            self.show_transfer_result(result)
                
        except Exception as e:
            logger.exception("Transfer error:")
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Critical,
                "Error",
                f"An error occurred during transfer:\n{e}"
            )
            msg.exec()
    
    def show_transfer_result(self, result):
        """Show detailed transfer result."""
        from result_dialog import ResultDialog
        
        dialog = ResultDialog(result, self)
        dialog.exec()
    
    def rename_selected_model(self, model: ModelInfo):
        """Rename a selected model."""
        if not model or not model.folder_path:
            return
        
        # Check VTS is closed
        msg = create_dark_messagebox(
            self,
            QMessageBox.Icon.Warning,
            "Close VTube Studio",
            "Please make sure VTube Studio is closed before renaming a model.\n\n"
            "Renaming while VTS is running may cause issues.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return
        
        # Show rename dialog
        dialog = ModelRenameDialog(model.name, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_name = dialog.new_name
        create_new_id = dialog.create_new_id
        
        # Validate rename
        is_valid, error = self.renamer.validate_rename(model.folder_path, new_name)
        if not is_valid:
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Critical,
                "Invalid Rename",
                f"Cannot rename model:\n\n{error}"
            )
            msg.exec()
            return
        
        # Execute rename
        logger.info(f"Renaming model: {model.name} → {new_name}")
        result = self.renamer.rename_model(model.folder_path, new_name, create_new_id)
        
        # Show result
        if result.success:
            # Show success message with details
            changes_text = "\n".join(f"• {change}" for change in result.changes_made)
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Information,
                "Rename Complete",
                f"Model renamed successfully!\n\n"
                f"Old name: {model.name}\n"
                f"New name: {new_name}\n\n"
                f"Changes made:\n{changes_text}\n\n"
                f"Backup created: {result.backup_path.name if result.backup_path else 'None'}"
            )
            msg.exec()
            
            # Refresh model list
            self.discover_vts()
        else:
            msg = create_dark_messagebox(
                self,
                QMessageBox.Icon.Critical,
                "Rename Failed",
                f"Failed to rename model:\n\n{result.error}\n\n"
                f"Check logs for details."
            )
            msg.exec()
