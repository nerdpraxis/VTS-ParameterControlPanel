"""
Backup Tab - Centralized backup and restore for VTS and OBS
"""

import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt

from backup_restore_widget import BackupRestoreWidget

logger = logging.getLogger(__name__)


class BackupTab(QWidget):
    """Tab for managing all backups (VTS, OBS, etc.)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        logger.info("Backup tab initialized")
    
    def setup_ui(self):
        """Setup the UI."""
        # Main layout with no margins (scroll area handles this)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
        """)
        
        # Content widget
        content = QWidget()
        content.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("<h1>Backup & Restore</h1>")
        header.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "Create and restore complete backups of your configurations.\n"
            "All backups are stored as ZIP files for easy portability."
        )
        desc.setStyleSheet("color: #cccccc; background-color: transparent; font-size: 11pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #3d3d3d;")
        layout.addWidget(separator)
        
        # VTS Backup Section
        vts_header = QLabel("<h2>VTube Studio Backup</h2>")
        vts_header.setStyleSheet("color: #ffffff; background-color: transparent;")
        layout.addWidget(vts_header)
        
        vts_desc = QLabel(
            "Backup your complete VTube Studio configuration including all models, "
            "items, settings, calibration data, and visual effects."
        )
        vts_desc.setStyleSheet("color: #cccccc; background-color: transparent;")
        vts_desc.setWordWrap(True)
        layout.addWidget(vts_desc)
        
        # VTS Backup widget
        self.vts_backup = BackupRestoreWidget()
        layout.addWidget(self.vts_backup)
        
        # === STREAMING SOFTWARE SECTION ===
        streaming_separator = QWidget()
        streaming_separator.setFixedHeight(2)
        streaming_separator.setStyleSheet("background-color: #3d3d3d;")
        layout.addWidget(streaming_separator)
        
        streaming_category = QLabel("<h2>🎥 Streaming Software</h2>")
        streaming_category.setStyleSheet("color: #ffffff; background-color: transparent; margin-top: 10px;")
        layout.addWidget(streaming_category)
        
        # OBS Studio
        obs_header = QLabel("<h3>OBS Studio</h3>")
        obs_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 5px;")
        layout.addWidget(obs_header)
        
        obs_placeholder = QLabel(
            "📦 Backup scenes, sources, settings, filters, and plugins"
        )
        obs_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        obs_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        obs_placeholder.setWordWrap(True)
        layout.addWidget(obs_placeholder)
        
        # Streamlabs Desktop
        streamlabs_header = QLabel("<h3>Streamlabs Desktop</h3>")
        streamlabs_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 10px;")
        layout.addWidget(streamlabs_header)
        
        streamlabs_placeholder = QLabel(
            "📦 Backup scenes, overlays, alerts, chatbot settings, and themes"
        )
        streamlabs_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        streamlabs_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        streamlabs_placeholder.setWordWrap(True)
        layout.addWidget(streamlabs_placeholder)
        
        # === AUDIO SOFTWARE SECTION ===
        audio_separator = QWidget()
        audio_separator.setFixedHeight(2)
        audio_separator.setStyleSheet("background-color: #3d3d3d; margin-top: 15px;")
        layout.addWidget(audio_separator)
        
        audio_category = QLabel("<h2>🎵 Audio Software</h2>")
        audio_category.setStyleSheet("color: #ffffff; background-color: transparent; margin-top: 10px;")
        layout.addWidget(audio_category)
        
        # VoiceMeeter
        voicemeeter_header = QLabel("<h3>VoiceMeeter (Banana/Potato)</h3>")
        voicemeeter_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 5px;")
        layout.addWidget(voicemeeter_header)
        
        voicemeeter_placeholder = QLabel(
            "📦 Backup audio routing, strips, buses, and macro buttons"
        )
        voicemeeter_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        voicemeeter_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        voicemeeter_placeholder.setWordWrap(True)
        layout.addWidget(voicemeeter_placeholder)
        
        # Voicemod
        voicemod_header = QLabel("<h3>Voicemod</h3>")
        voicemod_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 10px;")
        layout.addWidget(voicemod_header)
        
        voicemod_placeholder = QLabel(
            "📦 Backup voice effects, custom voices, soundboard, and keybinds"
        )
        voicemod_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        voicemod_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        voicemod_placeholder.setWordWrap(True)
        layout.addWidget(voicemod_placeholder)
        
        # === CONTROL SOFTWARE SECTION ===
        control_separator = QWidget()
        control_separator.setFixedHeight(2)
        control_separator.setStyleSheet("background-color: #3d3d3d; margin-top: 15px;")
        layout.addWidget(control_separator)
        
        control_category = QLabel("<h2>🎮 Control Software</h2>")
        control_category.setStyleSheet("color: #ffffff; background-color: transparent; margin-top: 10px;")
        layout.addWidget(control_category)
        
        # Stream Deck
        streamdeck_header = QLabel("<h3>Elgato Stream Deck</h3>")
        streamdeck_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 5px;")
        layout.addWidget(streamdeck_header)
        
        streamdeck_placeholder = QLabel(
            "📦 Backup profiles, buttons, actions, icons, and multi-actions"
        )
        streamdeck_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        streamdeck_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        streamdeck_placeholder.setWordWrap(True)
        layout.addWidget(streamdeck_placeholder)
        
        # Touch Portal
        touchportal_header = QLabel("<h3>Touch Portal</h3>")
        touchportal_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 10px;")
        layout.addWidget(touchportal_header)
        
        touchportal_placeholder = QLabel(
            "📦 Backup pages, buttons, actions, and custom plugins"
        )
        touchportal_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        touchportal_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        touchportal_placeholder.setWordWrap(True)
        layout.addWidget(touchportal_placeholder)
        
        # LioranBoard
        lioranboard_header = QLabel("<h3>LioranBoard</h3>")
        lioranboard_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 10px;")
        layout.addWidget(lioranboard_header)
        
        lioranboard_placeholder = QLabel(
            "📦 Backup decks, commands, triggers, and custom scripts"
        )
        lioranboard_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        lioranboard_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lioranboard_placeholder.setWordWrap(True)
        layout.addWidget(lioranboard_placeholder)
        
        # === VTUBER SOFTWARE SECTION ===
        vtuber_separator = QWidget()
        vtuber_separator.setFixedHeight(2)
        vtuber_separator.setStyleSheet("background-color: #3d3d3d; margin-top: 15px;")
        layout.addWidget(vtuber_separator)
        
        vtuber_category = QLabel("<h2>🎭 VTuber Software</h2>")
        vtuber_category.setStyleSheet("color: #ffffff; background-color: transparent; margin-top: 10px;")
        layout.addWidget(vtuber_category)
        
        # VSeeFace
        vseeface_header = QLabel("<h3>VSeeFace</h3>")
        vseeface_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 5px;")
        layout.addWidget(vseeface_header)
        
        vseeface_placeholder = QLabel(
            "📦 Backup avatars, tracking settings, expressions, and camera configs"
        )
        vseeface_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        vseeface_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vseeface_placeholder.setWordWrap(True)
        layout.addWidget(vseeface_placeholder)
        
        # Warudo
        warudo_header = QLabel("<h3>Warudo</h3>")
        warudo_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 10px;")
        layout.addWidget(warudo_header)
        
        warudo_placeholder = QLabel(
            "📦 Backup scenes, blueprints, assets, props, and settings"
        )
        warudo_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        warudo_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        warudo_placeholder.setWordWrap(True)
        layout.addWidget(warudo_placeholder)
        
        # === OTHER APPS SECTION ===
        other_separator = QWidget()
        other_separator.setFixedHeight(2)
        other_separator.setStyleSheet("background-color: #3d3d3d; margin-top: 15px;")
        layout.addWidget(other_separator)
        
        other_category = QLabel("<h2>💬 Communication & Misc</h2>")
        other_category.setStyleSheet("color: #ffffff; background-color: transparent; margin-top: 10px;")
        layout.addWidget(other_category)
        
        # Discord
        discord_header = QLabel("<h3>Discord</h3>")
        discord_header.setStyleSheet("color: #888888; background-color: transparent; margin-top: 5px;")
        layout.addWidget(discord_header)
        
        discord_placeholder = QLabel(
            "📦 Backup settings, keybinds, themes, and soundboard sounds"
        )
        discord_placeholder.setStyleSheet("""
            color: #666666; 
            background-color: #252525; 
            padding: 15px; 
            border: 2px dashed #3d3d3d;
            border-radius: 5px;
        """)
        discord_placeholder.setAlignment(Qt.AlignmentFlag.AlignLeft)
        discord_placeholder.setWordWrap(True)
        layout.addWidget(discord_placeholder)
        
        # Spacer
        layout.addStretch()
        
        # Set content to scroll area
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
