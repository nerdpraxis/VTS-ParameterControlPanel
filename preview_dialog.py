"""
Preview Dialog - Shows what will be transferred before applying
"""

import logging
from typing import List
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from vts_discovery import ModelInfo
from vts_file_parser import VTSFileParser
from model_settings_manager import TransferSettings, ModelSettingsManager

logger = logging.getLogger(__name__)


class PreviewDialog(QDialog):
    """Dialog for previewing transfer changes."""
    
    def __init__(
        self,
        source_model: ModelInfo,
        target_model: ModelInfo,
        settings: TransferSettings,
        parent=None
    ):
        super().__init__(parent)
        
        self.source_model = source_model
        self.target_model = target_model
        self.settings = settings
        
        self.setup_ui()
        self.generate_preview()
        self.apply_dark_theme()
        
        self.setWindowTitle("Transfer Preview")
        self.resize(700, 500)
    
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
            }
        """)
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<b>Transfer Preview</b>")
        header.setStyleSheet("color: #ffffff; font-size: 16px; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        layout.addWidget(header)
        
        # Model info
        model_info = QLabel(
            f"From: <b>{self.source_model.name}</b><br>"
            f"To: <b>{self.target_model.name}</b>"
        )
        model_info.setStyleSheet("color: #cccccc; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        layout.addWidget(model_info)
        
        # Preview text
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.preview_text, 1)
        
        # Info box
        info = QLabel(
            "ℹ This is a preview only. No changes will be made until you click 'Transfer' in the previous dialog."
        )
        info.setStyleSheet("color: #ffaa00; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def generate_preview(self):
        """Generate preview text."""
        lines = []
        
        lines.append("=" * 60)
        lines.append("TRANSFER PREVIEW")
        lines.append("=" * 60)
        lines.append("")
        
        # Backup info
        if self.settings.create_backup:
            lines.append("✓ Backup will be created:")
            backup_name = f"{self.target_model.vtube_json_path.stem}.backup_[timestamp].json"
            lines.append(f"  → backups/{backup_name}")
            lines.append("")
        else:
            lines.append("⚠ No backup will be created")
            lines.append("")
        
        # Hotkeys
        if self.settings.selected_hotkey_ids:
            lines.append(f"HOTKEYS TO TRANSFER: {len(self.settings.selected_hotkey_ids)}")
            lines.append("-" * 60)
            
            # Load source hotkeys
            source_data = VTSFileParser.load_vtube_json(self.source_model.vtube_json_path)
            if source_data:
                source_hotkeys = VTSFileParser.parse_hotkeys(source_data)
                
                for hotkey in source_hotkeys:
                    if hotkey.hotkey_id in self.settings.selected_hotkey_ids:
                        lines.append(f"  • {hotkey.name}")
                        lines.append(f"    Keybind: {hotkey.get_keybind_string()}")
                        lines.append(f"    Action: {hotkey.action}")
                        if hotkey.file:
                            lines.append(f"    File: {hotkey.file}")
                        
                        if self.settings.generate_new_ids:
                            lines.append(f"    ℹ New UUID will be generated")
                        
                        lines.append("")
            
            # Expression files
            if self.settings.copy_expression_files:
                lines.append("EXPRESSION FILES TO COPY:")
                lines.append("-" * 60)
                
                files_to_copy = set()
                for hotkey in source_hotkeys:
                    if hotkey.hotkey_id in self.settings.selected_hotkey_ids and hotkey.file:
                        files_to_copy.add(hotkey.file)
                
                if files_to_copy:
                    for file in sorted(files_to_copy):
                        source_file = self.source_model.folder_path / file
                        target_file = self.target_model.folder_path / file
                        
                        if source_file.exists():
                            if target_file.exists():
                                lines.append(f"  ⚠ {file} (already exists in target - will skip)")
                            else:
                                lines.append(f"  ✓ {file}")
                        else:
                            lines.append(f"  ✗ {file} (not found in source)")
                    lines.append("")
                else:
                    lines.append("  (none)")
                    lines.append("")
        
        # Parameters
        if self.settings.selected_parameter_names:
            lines.append(f"PARAMETERS TO TRANSFER: {len(self.settings.selected_parameter_names)}")
            lines.append("-" * 60)
            
            # Load source parameters
            source_data = VTSFileParser.load_vtube_json(self.source_model.vtube_json_path)
            if source_data:
                source_params = VTSFileParser.parse_parameters(source_data)
                
                for param in source_params:
                    if param.name in self.settings.selected_parameter_names:
                        lines.append(f"  • {param.name}")
                        lines.append(f"    Input: {param.input_param}")
                        lines.append(f"    Output: {param.output_param}")
                        lines.append(f"    Range: {param.output_range[0]:.1f} to {param.output_range[1]:.1f}")
                        lines.append(f"    Smoothing: {param.smoothing}")
                        lines.append("")
        
        # Summary
        lines.append("=" * 60)
        lines.append("SUMMARY")
        lines.append("=" * 60)
        
        total_items = len(self.settings.selected_hotkey_ids) + len(self.settings.selected_parameter_names)
        lines.append(f"Total items to transfer: {total_items}")
        lines.append(f"  • Hotkeys: {len(self.settings.selected_hotkey_ids)}")
        lines.append(f"  • Parameters: {len(self.settings.selected_parameter_names)}")
        
        if self.settings.copy_expression_files:
            lines.append(f"  • Expression files will be copied")
        
        lines.append("")
        
        if self.settings.create_backup:
            lines.append("✓ Backup will be created before making changes")
        else:
            lines.append("⚠ NO BACKUP will be created")
        
        if self.settings.generate_new_ids:
            lines.append("✓ New hotkey UUIDs will be generated")
        else:
            lines.append("⚠ Original hotkey UUIDs will be kept (may cause conflicts)")
        
        lines.append("")
        lines.append("=" * 60)
        
        # Set text
        self.preview_text.setPlainText("\n".join(lines))
