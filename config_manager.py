"""
Configuration manager for VTS Control Panel
Simplified version of AIKA's config_utils
"""

import os
import logging
from configparser import ConfigParser

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for VTS Control Panel."""
    
    def __init__(self, config_file='config.ini'):
        """Initialize config manager."""
        self.config_file = config_file
        self.config = ConfigParser()
        self.load()
    
    def load(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file)
                logger.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.create_default()
        else:
            self.create_default()
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            logger.info(f"Saved config to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def create_default(self):
        """Create default configuration."""
        self.config['VTS'] = {
            'api_url': 'ws://localhost:8001/',
            'auth_token': '',
            'auto_connect': 'false',
            'params_json': 'custom_params.json'
        }
        
        self.config['UI'] = {
            'window_width': '900',
            'window_height': '700',
            'window_x': '100',
            'window_y': '100'
        }
        
        self.save()
        logger.info("Created default configuration")
    
    def get_string(self, section: str, option: str, fallback: str = '') -> str:
        """Get string value from config."""
        return self.config.get(section, option, fallback=fallback)
    
    def get_int(self, section: str, option: str, fallback: int = 0) -> int:
        """Get integer value from config."""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except:
            return fallback
    
    def get_float(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Get float value from config."""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except:
            return fallback
    
    def get_bool(self, section: str, option: str, fallback: bool = False) -> bool:
        """Get boolean value from config."""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except:
            return fallback
    
    def set_value(self, section: str, option: str, value):
        """Set value in config."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
