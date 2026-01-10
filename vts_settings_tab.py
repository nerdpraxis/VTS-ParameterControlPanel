"""
VTS Settings Tab - Connection and configuration
"""

import logging
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QCheckBox, QGroupBox,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

from vts_service import VTSService

logger = logging.getLogger(__name__)


class ConnectionWorker(QThread):
    """Worker thread for VTS connection/disconnection."""
    
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, vts_service, action='connect'):
        super().__init__()
        self.vts_service = vts_service
        self.action = action
    
    def run(self):
        """Run connection/disconnection in thread."""
        try:
            # Use the VTS service's persistent loop if connecting
            # or create temp loop for disconnecting
            if self.action == 'connect':
                # Start the persistent loop first if not already started
                if not self.vts_service._loop:
                    self.vts_service._start_event_loop()
                
                # Schedule connection on the persistent loop
                import asyncio
                future = asyncio.run_coroutine_threadsafe(
                    self.vts_service.connect(),
                    self.vts_service._loop
                )
                success = future.result(timeout=10.0)
                
                if success:
                    self.finished.emit(True, "Connected to VTube Studio!")
                else:
                    self.finished.emit(False, "Failed to connect to VTube Studio")
            else:
                # For disconnect, use a temp loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.vts_service.disconnect())
                loop.close()
                self.finished.emit(True, "Disconnected from VTube Studio")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.finished.emit(False, f"Error: {str(e)}")


class VTSSettingsTab(QWidget):
    """Settings tab for VTS connection."""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.vts_service = VTSService(config_manager)
        self.connection_worker = None
        
        self.create_layout()
        self.load_settings()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_connection_status)
        self.status_timer.start(1000)  # Update every second
        
        # Auto-connect if enabled
        if self.auto_connect_checkbox.isChecked():
            QTimer.singleShot(500, self.toggle_connection)
    
    def create_layout(self):
        """Create the settings UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Connection settings group
        connection_group = QGroupBox("VTube Studio Connection")
        connection_layout = QFormLayout()
        
        # API URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("ws://localhost:8001/")
        self.url_input.textChanged.connect(self.save_settings)
        connection_layout.addRow("API URL:", self.url_input)
        
        # Auto-connect
        self.auto_connect_checkbox = QCheckBox()
        self.auto_connect_checkbox.stateChanged.connect(self.save_settings)
        connection_layout.addRow("Auto-connect on startup:", self.auto_connect_checkbox)
        
        # Connection status
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: #ff6b6b;")
        connection_layout.addRow("Status:", self.status_label)
        
        # Connect button
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.connect_button.setMinimumHeight(40)
        button_layout.addWidget(self.connect_button)
        
        connection_layout.addRow("", button_layout)
        connection_group.setLayout(connection_layout)
        
        layout.addWidget(connection_group)
        layout.addStretch()
        
        # Apply dark theme
        self.setStyleSheet("""
            QGroupBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                color: #ffffff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: #ffffff;
                border: none;
                border-radius: 3px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #808080;
            }
        """)
    
    def load_settings(self):
        """Load settings from config."""
        url = self.config.get_string('VTS', 'api_url', 'ws://localhost:8001/')
        auto_connect = self.config.get_bool('VTS', 'auto_connect', False)
        
        self.url_input.setText(url)
        self.auto_connect_checkbox.setChecked(auto_connect)
    
    def save_settings(self):
        """Save settings to config."""
        self.config.set_value('VTS', 'api_url', self.url_input.text())
        self.config.set_value('VTS', 'auto_connect', self.auto_connect_checkbox.isChecked())
        self.config.save()
    
    def toggle_connection(self):
        """Toggle VTS connection."""
        if self.vts_service.is_authenticated():
            # Disconnect
            self.connect_button.setEnabled(False)
            self.connect_button.setText("Disconnecting...")
            
            self.connection_worker = ConnectionWorker(self.vts_service, 'disconnect')
            self.connection_worker.finished.connect(self.on_connection_finished)
            self.connection_worker.start()
        else:
            # Connect
            self.connect_button.setEnabled(False)
            self.connect_button.setText("Connecting...")
            
            self.connection_worker = ConnectionWorker(self.vts_service, 'connect')
            self.connection_worker.finished.connect(self.on_connection_finished)
            self.connection_worker.start()
    
    def on_connection_finished(self, success, message):
        """Handle connection result."""
        self.connect_button.setEnabled(True)
        
        if self.vts_service.is_authenticated():
            self.connect_button.setText("Disconnect")
            self.status_label.setText("Connected ✓")
            self.status_label.setStyleSheet("color: #51cf66;")
        else:
            self.connect_button.setText("Connect")
            self.status_label.setText("Not connected")
            self.status_label.setStyleSheet("color: #ff6b6b;")
        
        if not success:
            QMessageBox.warning(self, "Connection Error", message)
        else:
            logger.info(message)
    
    def update_connection_status(self):
        """Update connection status display."""
        if self.vts_service.is_authenticated():
            if self.status_label.text() != "Connected ✓":
                self.status_label.setText("Connected ✓")
                self.status_label.setStyleSheet("color: #51cf66;")
                self.connect_button.setText("Disconnect")
        else:
            if self.status_label.text() != "Not connected":
                self.status_label.setText("Not connected")
                self.status_label.setStyleSheet("color: #ff6b6b;")
                self.connect_button.setText("Connect")
    
    def cleanup(self):
        """Cleanup on close."""
        self.status_timer.stop()
        
        if self.vts_service.is_authenticated():
            # Disconnect synchronously
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.vts_service.disconnect())
                loop.close()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
