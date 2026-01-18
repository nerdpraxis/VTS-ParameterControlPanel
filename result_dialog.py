"""
Result Dialog - Shows detailed transfer results
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from model_settings_manager import TransferResult

logger = logging.getLogger(__name__)


class RestoreResultDialog(QDialog):
    """Dialog for displaying restore results."""
    
    def __init__(self, report, parent=None):
        super().__init__(parent)
        
        self.report = report
        
        self.setup_ui()
        self.apply_dark_theme()
        self.setWindowTitle("Restore Results")
        self.resize(700, 400)
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Status header
        if self.report.success:
            status_text = "✓ Restore Completed"
            status_color = "#00ff00"
        else:
            status_text = "✗ Restore Failed"
            status_color = "#ff0000"
        
        header = QLabel(f"<b>{status_text}</b>")
        header.setStyleSheet(f"color: {status_color}; font-size: 16px; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        layout.addWidget(header)
        
        # Summary
        summary_text = f"""
<b>Files Restored:</b> {self.report.files_restored}<br>
<b>Files Skipped:</b> {self.report.files_skipped}
        """.strip()
        
        if self.report.pre_restore_backup_path:
            summary_text += f"<br><b>Pre-restore Backup:</b> {self.report.pre_restore_backup_path.name}"
        
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("color: #cccccc; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        layout.addWidget(summary_label)
        
        # Log
        log_label = QLabel("<b>Detailed Log:</b>")
        log_label.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(log_label)
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setPlainText("\n".join(self.report.detailed_log))
        log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(log_text, 1)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
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


class ResultDialog(QDialog):
    """Dialog for displaying transfer results."""
    
    def __init__(self, result: TransferResult, parent=None):
        super().__init__(parent)
        
        self.result = result
        
        self.setup_ui()
        self.apply_dark_theme()
        self.setWindowTitle("Transfer Results")
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
        
        # Status header
        if self.result.success:
            status_text = "✓ Transfer Completed Successfully"
            status_color = "#00ff00"
        else:
            status_text = "✗ Transfer Failed"
            status_color = "#ff0000"
        
        header = QLabel(f"<b>{status_text}</b>")
        header.setStyleSheet(f"color: {status_color}; font-size: 16px; background-color: #2d2d2d; padding: 10px; border-radius: 5px;")
        layout.addWidget(header)
        
        # Summary
        summary_group = QGroupBox("Summary")
        summary_group.setStyleSheet("""
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
        summary_layout = QVBoxLayout(summary_group)
        
        summary_text = f"""
<b>Changes:</b> {self.result.changes_summary}<br>
<b>Hotkeys Added:</b> {self.result.hotkeys_added}<br>
<b>Parameters Added:</b> {self.result.parameters_added}<br>
<b>Files Copied:</b> {self.result.files_copied}
        """.strip()
        
        if self.result.backup_path:
            summary_text += f"<br><b>Backup:</b> {self.result.backup_path.name}"
        
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        summary_layout.addWidget(summary_label)
        
        layout.addWidget(summary_group)
        
        # Warnings
        if self.result.warnings:
            warnings_group = QGroupBox(f"Warnings ({len(self.result.warnings)})")
            warnings_group.setStyleSheet("""
                QGroupBox {
                    color: #ffaa00;
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
            warnings_layout = QVBoxLayout(warnings_group)
            
            warnings_text = QTextEdit()
            warnings_text.setReadOnly(True)
            warnings_text.setMaximumHeight(100)
            warnings_text.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffaa00;
                    border: 1px solid #3d3d3d;
                    font-family: 'Consolas', 'Courier New', monospace;
                }
            """)
            warnings_text.setPlainText("\n".join(f"⚠ {w}" for w in self.result.warnings))
            warnings_layout.addWidget(warnings_text)
            
            layout.addWidget(warnings_group)
        
        # Errors
        if self.result.errors:
            errors_group = QGroupBox(f"Errors ({len(self.result.errors)})")
            errors_group.setStyleSheet("""
                QGroupBox {
                    color: #ff0000;
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
            errors_layout = QVBoxLayout(errors_group)
            
            errors_text = QTextEdit()
            errors_text.setReadOnly(True)
            errors_text.setMaximumHeight(100)
            errors_text.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ff0000;
                    border: 1px solid #3d3d3d;
                    font-family: 'Consolas', 'Courier New', monospace;
                }
            """)
            errors_text.setPlainText("\n".join(f"✗ {e}" for e in self.result.errors))
            errors_layout.addWidget(errors_text)
            
            layout.addWidget(errors_group)
        
        # Detailed log
        log_group = QGroupBox("Detailed Log")
        log_group.setStyleSheet("""
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
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        self.log_text.setPlainText("\n".join(self.result.detailed_log))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if self.result.success and self.result.can_undo and self.result.undo_backup_path:
            undo_btn = QPushButton("Undo Transfer (Restore Backup)")
            undo_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffaa00;
                    color: #000000;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #ffcc00;
                }
            """)
            undo_btn.clicked.connect(self.undo_transfer)
            button_layout.addWidget(undo_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def undo_transfer(self):
        """Undo the transfer by restoring the backup."""
        from PyQt6.QtWidgets import QMessageBox
        from model_settings_manager import ModelSettingsManager
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Undo")
        msg.setText("This will restore the target model to its state before the transfer.\n\nContinue?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get target path from backup path
            # backup path is like: backups/ModelName.backup_timestamp.json
            # need to restore to the original .vtube.json location
            
            info_msg = QMessageBox(self)
            info_msg.setIcon(QMessageBox.Icon.Information)
            info_msg.setWindowTitle("Undo")
            info_msg.setText(
                "To manually undo:\n\n"
                f"1. Find the backup file: {self.result.undo_backup_path.name}\n"
                f"2. Copy it to the model folder\n"
                f"3. Rename it to replace the .vtube.json file\n\n"
                "Automatic undo will be implemented in a future update."
            )
            info_msg.setStyleSheet("""
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
            info_msg.exec()
