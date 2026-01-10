"""
VTS Parameters Tab - Wraps AIKA's VTSParamsComponent
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt

# Add parent directory to import AIKA's components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.vts_params import VTSParamsComponent
from ui.theme import theme

logger = logging.getLogger(__name__)


class VTSParamsTab(QWidget):
    """Tab containing VTS parameters management."""
    
    def __init__(self, config_manager, vts_service):
        super().__init__()
        self.config = config_manager
        self.vts_service = vts_service
        
        # Set dark background for the tab itself
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.COLORS['primary']};
            }}
        """)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Get params JSON path from config
        params_json = self.config.get_string('VTS', 'params_json', 'custom_params.json')
        
        # Create scroll area for params component
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {theme.COLORS['primary']};
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {theme.COLORS['primary']};
            }}
        """)
        
        # Create AIKA's VTS params component
        self.vts_params = VTSParamsComponent(json_file_path=params_json)
        
        # Set VTS service
        self.vts_params.set_vts_service(vts_service)
        
        scroll.setWidget(self.vts_params)
        layout.addWidget(scroll)
        
        logger.info("VTS Parameters tab initialized")
