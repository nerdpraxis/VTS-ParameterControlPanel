"""
Backup & Restore Widget - UI for complete VTS configuration backup/restore
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QCheckBox, QTextEdit, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from vts_backup_manager import VTSBackupManager, BackupOptions, RestoreOptions
from vts_discovery import get_vts_discovery

logger = logging.getLogger(__name__)


class BackupThread(QThread):
    """Thread for creating backups."""
    finished = pyqtSignal(object)  # Path or None
    error = pyqtSignal(str)
    
    def __init__(self, manager, vts_root, output_path, options):
        super().__init__()
        self.manager = manager
        self.vts_root = vts_root
        self.output_path = output_path
        self.options = options
    
    def run(self):
        try:
            result = self.manager.create_backup(self.vts_root, self.output_path, self.options)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class RestoreThread(QThread):
    """Thread for restoring backups."""
    finished = pyqtSignal(object)  # RestoreReport
    error = pyqtSignal(str)
    
    def __init__(self, manager, backup_path, vts_root, options):
        super().__init__()
        self.manager = manager
        self.backup_path = backup_path
        self.vts_root = vts_root
        self.options = options
    
    def run(self):
        try:
            result = self.manager.restore_backup(self.backup_path, self.vts_root, self.options)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BackupRestoreWidget(QWidget):
    """Widget for VTS complete backup and restore."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.manager = VTSBackupManager()
        self.discovery = get_vts_discovery()
        self.backup_thread = None
        self.restore_thread = None
        
        # Remember last backup location
        self.last_backup_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create backup section
        backup_group = self.create_backup_section()
        layout.addWidget(backup_group)
        
        # Restore section
        restore_group = self.create_restore_section()
        layout.addWidget(restore_group)
    
    def create_backup_section(self) -> QGroupBox:
        """Create backup section."""
        group = QGroupBox("Create Backup")
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
        
        # Options checkboxes
        self.backup_global_check = QCheckBox("Global settings (vts_config.json)")
        self.backup_global_check.setChecked(True)
        self.backup_global_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_global_check)
        
        self.backup_models_check = QCheckBox("All model configs")
        self.backup_models_check.setChecked(True)
        self.backup_models_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_models_check)
        
        self.backup_items_check = QCheckBox("All item configs")
        self.backup_items_check.setChecked(True)
        self.backup_items_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_items_check)
        
        self.backup_params_check = QCheckBox("Custom parameters")
        self.backup_params_check.setChecked(True)
        self.backup_params_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_params_check)
        
        self.backup_calibration_check = QCheckBox("Calibration data")
        self.backup_calibration_check.setChecked(True)
        self.backup_calibration_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_calibration_check)
        
        self.backup_effects_check = QCheckBox("Visual effects settings")
        self.backup_effects_check.setChecked(True)
        self.backup_effects_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.backup_effects_check)
        
        self.backup_auth_check = QCheckBox("Plugin auth tokens (⚠ sensitive)")
        self.backup_auth_check.setChecked(False)
        self.backup_auth_check.setStyleSheet("color: #ffaa00; background-color: transparent;")
        layout.addWidget(self.backup_auth_check)
        
        # Notes
        notes_label = QLabel("Notes (optional):")
        notes_label.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(notes_label)
        
        self.backup_notes = QTextEdit()
        self.backup_notes.setPlaceholderText("Add notes about this backup...")
        self.backup_notes.setMaximumHeight(60)
        self.backup_notes.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
            }
        """)
        layout.addWidget(self.backup_notes)
        
        # Create button
        self.create_backup_btn = QPushButton("Create Backup ZIP...")
        self.create_backup_btn.setStyleSheet("""
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
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.create_backup_btn.clicked.connect(self.create_backup)
        layout.addWidget(self.create_backup_btn)
        
        # Progress bar
        self.backup_progress = QProgressBar()
        self.backup_progress.setVisible(False)
        self.backup_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        layout.addWidget(self.backup_progress)
        
        return group
    
    def create_restore_section(self) -> QGroupBox:
        """Create restore section."""
        group = QGroupBox("Restore from Backup")
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
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.backup_file_label = QLabel("No backup file selected")
        self.backup_file_label.setStyleSheet("color: #cccccc; background-color: transparent;")
        file_layout.addWidget(self.backup_file_label, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet("""
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
        browse_btn.clicked.connect(self.browse_backup_file)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Options
        self.restore_pre_backup_check = QCheckBox("Create backup before restoring (recommended)")
        self.restore_pre_backup_check.setChecked(True)
        self.restore_pre_backup_check.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(self.restore_pre_backup_check)
        
        # Warning
        warning_label = QLabel("⚠ Warning: Restoring will overwrite your current VTS settings.\nMake sure VTube Studio is closed before restoring!")
        warning_label.setStyleSheet("color: #ffaa00; background-color: transparent; padding: 10px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # Restore button
        self.restore_btn = QPushButton("Restore from ZIP")
        self.restore_btn.setEnabled(False)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc6600;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff8800;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        self.restore_btn.clicked.connect(self.restore_backup)
        layout.addWidget(self.restore_btn)
        
        # Progress bar
        self.restore_progress = QProgressBar()
        self.restore_progress.setVisible(False)
        self.restore_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #ffffff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #cc6600;
            }
        """)
        layout.addWidget(self.restore_progress)
        
        return group
    
    def create_backup(self):
        """Create a backup."""
        if not self.discovery.vts_root:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("VTS Not Found")
            msg.setText("VTube Studio installation not found.")
            msg.setStyleSheet("QMessageBox { background-color: #1e1e1e; color: #ffffff; }")
            msg.exec()
            return
        
        # Ask for save location
        suggested_name = f"vts_backup_{Path.home().name}.zip"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Backup As",
            str(Path.home() / suggested_name),
            "ZIP Files (*.zip)"
        )
        
        if not file_path:
            return
        
        # Build options
        options = BackupOptions(
            include_global_config=self.backup_global_check.isChecked(),
            include_model_configs=self.backup_models_check.isChecked(),
            include_item_configs=self.backup_items_check.isChecked(),
            include_custom_parameters=self.backup_params_check.isChecked(),
            include_calibration=self.backup_calibration_check.isChecked(),
            include_plugin_auth=self.backup_auth_check.isChecked(),
            include_visual_effects=self.backup_effects_check.isChecked(),
            user_notes=self.backup_notes.toPlainText(),
            backup_reason="manual"
        )
        
        # Show progress
        self.backup_progress.setVisible(True)
        self.backup_progress.setRange(0, 0)  # Indeterminate
        self.create_backup_btn.setEnabled(False)
        
        # Create backup in thread
        self.backup_thread = BackupThread(
            self.manager,
            self.discovery.vts_root,
            Path(file_path),
            options
        )
        self.backup_thread.finished.connect(self.on_backup_finished)
        self.backup_thread.error.connect(self.on_backup_error)
        self.backup_thread.start()
    
    def on_backup_finished(self, backup_path):
        """Handle backup completion."""
        self.backup_progress.setVisible(False)
        self.create_backup_btn.setEnabled(True)
        
        if backup_path:
            self.last_backup_path = backup_path
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Backup Complete")
            msg.setText(f"Backup created successfully!\n\n{backup_path}")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #007acc; color: #ffffff; }
            """)
            msg.exec()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Backup Failed")
            msg.setText("Failed to create backup. Check logs for details.")
            msg.setStyleSheet("""
                QMessageBox { background-color: #1e1e1e; color: #ffffff; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; }
            """)
            msg.exec()
    
    def on_backup_error(self, error):
        """Handle backup error."""
        self.backup_progress.setVisible(False)
        self.create_backup_btn.setEnabled(True)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Backup Error")
        msg.setText(f"An error occurred during backup:\n\n{error}")
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #3d3d3d; color: #ffffff; }
        """)
        msg.exec()
    
    def browse_backup_file(self):
        """Browse for backup file to restore."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            str(Path.home()),
            "ZIP Files (*.zip)"
        )
        
        if file_path:
            self.last_backup_path = Path(file_path)
            self.backup_file_label.setText(Path(file_path).name)
            self.restore_btn.setEnabled(True)
    
    def restore_backup(self):
        """Restore from backup."""
        if not self.last_backup_path or not self.discovery.vts_root:
            return
        
        # Confirm
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Confirm Restore")
        msg.setText(
            "This will restore your VTS configuration from the backup.\n\n"
            "⚠ Your current settings will be overwritten!\n\n"
            "Make sure VTube Studio is closed before proceeding.\n\n"
            "Continue?"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #3d3d3d; color: #ffffff; }
        """)
        
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return
        
        # Build options
        options = RestoreOptions(
            create_pre_restore_backup=self.restore_pre_backup_check.isChecked()
        )
        
        # Show progress
        self.restore_progress.setVisible(True)
        self.restore_progress.setRange(0, 0)  # Indeterminate
        self.restore_btn.setEnabled(False)
        
        # Restore in thread
        self.restore_thread = RestoreThread(
            self.manager,
            self.last_backup_path,
            self.discovery.vts_root,
            options
        )
        self.restore_thread.finished.connect(self.on_restore_finished)
        self.restore_thread.error.connect(self.on_restore_error)
        self.restore_thread.start()
    
    def on_restore_finished(self, report):
        """Handle restore completion."""
        self.restore_progress.setVisible(False)
        self.restore_btn.setEnabled(True)
        
        # Show results
        from result_dialog import RestoreResultDialog
        dialog = RestoreResultDialog(report, self)
        dialog.exec()
    
    def on_restore_error(self, error):
        """Handle restore error."""
        self.restore_progress.setVisible(False)
        self.restore_btn.setEnabled(True)
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Restore Error")
        msg.setText(f"An error occurred during restore:\n\n{error}")
        msg.setStyleSheet("""
            QMessageBox { background-color: #1e1e1e; color: #ffffff; }
            QLabel { color: #ffffff; }
            QPushButton { background-color: #3d3d3d; color: #ffffff; }
        """)
        msg.exec()
