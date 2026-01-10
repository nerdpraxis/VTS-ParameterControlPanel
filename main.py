"""
VTS Control Panel - Standalone VTube Studio Parameter Controller
Simplified version of AIKA's VTS functionality
"""

import sys
import os
import logging
import asyncio
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vts_control_panel.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Windows console UTF-8 fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigManager
from vts_params_tab import VTSParamsTab
from vts_settings_tab import VTSSettingsTab

class VTSControlPanel(QMainWindow):
    """Main window for VTS Control Panel."""
    
    def __init__(self):
        super().__init__()
        
        # Determine config path (next to exe or script)
        if getattr(sys, 'frozen', False):
            # Running as exe
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        os.chdir(self.app_dir)
        logger.info(f"Working directory: {self.app_dir}")
        
        # Initialize config
        self.config_manager = ConfigManager('config.ini')
        
        # Setup UI
        self.setWindowTitle("VTS Control Panel")
        self.setWindowIcon(QIcon())  # TODO: Add icon
        
        # Restore window geometry
        self.restore_geometry()
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.settings_tab = VTSSettingsTab(self.config_manager)
        self.params_tab = VTSParamsTab(self.config_manager, self.settings_tab.vts_service)
        
        # Add tabs
        self.tabs.addTab(self.params_tab, "VTS Parameters")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Apply theme
        self.apply_theme()
        
        logger.info("VTS Control Panel initialized")
    
    def apply_theme(self):
        """Apply dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #252525;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
        """)
    
    def restore_geometry(self):
        """Restore window geometry from config."""
        width = self.config_manager.get_int('UI', 'window_width', 900)
        height = self.config_manager.get_int('UI', 'window_height', 700)
        x = self.config_manager.get_int('UI', 'window_x', 100)
        y = self.config_manager.get_int('UI', 'window_y', 100)
        
        self.setGeometry(x, y, width, height)
    
    def save_geometry(self):
        """Save window geometry to config."""
        geometry = self.geometry()
        self.config_manager.set_value('UI', 'window_width', geometry.width())
        self.config_manager.set_value('UI', 'window_height', geometry.height())
        self.config_manager.set_value('UI', 'window_x', geometry.x())
        self.config_manager.set_value('UI', 'window_y', geometry.y())
        self.config_manager.save()
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.save_geometry()
        
        # Cleanup
        if self.settings_tab:
            self.settings_tab.cleanup()
        
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("VTS Control Panel")
    
    window = VTSControlPanel()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
