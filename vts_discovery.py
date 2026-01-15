"""
VTS Discovery - Discovers VTube Studio installation and models
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from PyQt6.QtGui import QPixmap

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Information about a VTube Studio model."""
    
    name: str
    model_id: str
    folder_path: Path
    vtube_json_path: Path
    icon_path: Optional[Path]
    thumbnail: Optional[QPixmap]
    hotkey_count: int
    parameter_count: int
    expression_count: int
    last_modified: Optional[str]
    
    def __str__(self):
        return f"Model: {self.name} (ID: {self.model_id[:8]}..., {self.hotkey_count} hotkeys, {self.parameter_count} params)"


@dataclass
class ItemInfo:
    """Information about a VTube Studio item/accessory."""
    
    name: str
    model_id: str
    folder_path: Path
    vtube_json_path: Path
    icon_path: Optional[Path]
    thumbnail: Optional[QPixmap]
    hotkey_count: int
    
    def __str__(self):
        return f"Item: {self.name} (ID: {self.model_id[:8]}..., {self.hotkey_count} hotkeys)"


class VTSDiscovery:
    """Discovers VTube Studio installation and enumerates models/items."""
    
    def __init__(self):
        self.vts_root: Optional[Path] = None
        self.streaming_assets_path: Optional[Path] = None
        self.models_path: Optional[Path] = None
        self.items_path: Optional[Path] = None
        self.config_path: Optional[Path] = None
        
    def find_vts_installation(self, manual_path: Optional[Path] = None) -> bool:
        """
        Find VTube Studio installation.
        
        Args:
            manual_path: Optional manual path to VTS installation
            
        Returns:
            True if installation found, False otherwise
        """
        if manual_path:
            return self._validate_vts_path(manual_path)
        
        # Try common installation paths
        common_paths = [
            # Steam default
            Path("C:/Program Files (x86)/Steam/steamapps/common/Vtube Studio"),
            Path("C:/Program Files/Steam/steamapps/common/Vtube Studio"),
            
            # Standalone
            Path.home() / "VTube Studio",
            Path("C:/Program Files/VTube Studio"),
            Path("C:/Program Files (x86)/VTube Studio"),
            
            # User's Documents
            Path.home() / "Documents/VTube Studio",
        ]
        
        for path in common_paths:
            if self._validate_vts_path(path):
                logger.info(f"✓ Found VTube Studio installation at: {path}")
                return True
        
        logger.warning("⚠ VTube Studio installation not found in common locations")
        return False
    
    def _validate_vts_path(self, path: Path) -> bool:
        """
        Validate that the path contains a VTS installation.
        
        Args:
            path: Path to validate
            
        Returns:
            True if valid VTS installation, False otherwise
        """
        if not path.exists():
            return False
        
        # Check for VTube Studio_Data/StreamingAssets
        streaming_assets = path / "VTube Studio_Data" / "StreamingAssets"
        if not streaming_assets.exists():
            return False
        
        # Check for required folders
        config_folder = streaming_assets / "Config"
        models_folder = streaming_assets / "Live2DModels"
        
        if not config_folder.exists() or not models_folder.exists():
            return False
        
        # Valid installation found
        self.vts_root = path
        self.streaming_assets_path = streaming_assets
        self.models_path = models_folder
        self.items_path = streaming_assets / "Items"
        self.config_path = config_folder
        
        return True
    
    def get_models_list(self) -> List[ModelInfo]:
        """
        Get list of all installed models.
        
        Returns:
            List of ModelInfo objects
        """
        if not self.models_path or not self.models_path.exists():
            logger.warning("Models path not found")
            return []
        
        models = []
        skipped_folders = []
        
        # Scan all folders in Live2DModels
        for model_folder in self.models_path.iterdir():
            if not model_folder.is_dir():
                continue
            
            # Skip backup folders
            if model_folder.name.startswith('.') or model_folder.name.lower() in ['backup', 'backups']:
                logger.debug(f"Skipping backup/hidden folder: {model_folder.name}")
                continue
            
            # Find .vtube.json file in folder
            vtube_json_files = list(model_folder.glob("*.vtube.json"))
            if not vtube_json_files:
                logger.debug(f"No .vtube.json found in {model_folder.name}")
                skipped_folders.append(model_folder.name)
                continue
            
            # Use first .vtube.json file found (skip backup files)
            vtube_json_path = None
            for vj_file in vtube_json_files:
                # Skip backup files
                if '.original' in vj_file.name or '.backup' in vj_file.name or ' - Kopie' in vj_file.name:
                    logger.debug(f"Skipping backup file: {vj_file.name}")
                    continue
                vtube_json_path = vj_file
                break
            
            if not vtube_json_path:
                logger.debug(f"Only backup .vtube.json files found in {model_folder.name}")
                skipped_folders.append(model_folder.name)
                continue
            
            try:
                # Parse basic info from the file
                model_info = self._parse_model_info(vtube_json_path, model_folder)
                if model_info:
                    models.append(model_info)
                    logger.info(f"✓ Loaded model: {model_info.name}")
                else:
                    logger.warning(f"Failed to parse model info from {vtube_json_path.name}")
                    skipped_folders.append(model_folder.name)
            except Exception as e:
                logger.error(f"Error parsing model {vtube_json_path.name}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                skipped_folders.append(model_folder.name)
                continue
        
        logger.info(f"✓ Found {len(models)} models")
        if skipped_folders:
            logger.info(f"⚠ Skipped {len(skipped_folders)} folders: {', '.join(skipped_folders)}")
        
        return models
    
    def get_items_list(self) -> List[ItemInfo]:
        """
        Get list of all installed items/accessories.
        
        Returns:
            List of ItemInfo objects
        """
        if not self.items_path or not self.items_path.exists():
            logger.warning("Items path not found")
            return []
        
        items = []
        
        # Scan all folders in Items
        for item_folder in self.items_path.iterdir():
            if not item_folder.is_dir():
                continue
            
            # Find .vtube.json file in folder
            vtube_json_files = list(item_folder.glob("*.vtube.json"))
            if not vtube_json_files:
                continue
            
            # Use first .vtube.json file found
            vtube_json_path = vtube_json_files[0]
            
            try:
                # Parse basic info from the file
                item_info = self._parse_item_info(vtube_json_path, item_folder)
                if item_info:
                    items.append(item_info)
            except Exception as e:
                logger.error(f"Error parsing item {vtube_json_path.name}: {e}")
                continue
        
        logger.info(f"✓ Found {len(items)} items")
        return items
    
    def _parse_model_info(self, vtube_json_path: Path, model_folder: Path) -> Optional[ModelInfo]:
        """
        Parse basic info from a model's .vtube.json file.
        
        Args:
            vtube_json_path: Path to .vtube.json file
            model_folder: Path to model folder
            
        Returns:
            ModelInfo object or None if parsing failed
        """
        import json
        
        try:
            # Load JSON
            with open(vtube_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if this is a valid VTube Studio config
            if 'Version' not in data and 'ModelID' not in data:
                logger.warning(f"File {vtube_json_path.name} doesn't appear to be a valid .vtube.json file")
                return None
            
            # Extract basic info with fallbacks
            name = data.get('Name', vtube_json_path.stem)
            model_id = data.get('ModelID', 'unknown')
            
            # Validate name
            if not name or name.strip() == '':
                name = vtube_json_path.stem
            
            # Count hotkeys and parameters
            hotkeys = data.get('Hotkeys', [])
            parameters = data.get('ParameterSettings', [])
            
            if not isinstance(hotkeys, list):
                logger.warning(f"Invalid Hotkeys format in {vtube_json_path.name}")
                hotkeys = []
            
            if not isinstance(parameters, list):
                logger.warning(f"Invalid ParameterSettings format in {vtube_json_path.name}")
                parameters = []
            
            # Count expression files in folder
            expression_count = 0
            try:
                expression_count = len(list(model_folder.glob("*.exp3.json")))
            except Exception as e:
                logger.debug(f"Could not count expressions for {name}: {e}")
            
            # Find icon
            icon_path = None
            try:
                file_refs = data.get('FileReferences', {})
                icon_name = file_refs.get('Icon', 'icon.png')
                potential_icon = model_folder / icon_name
                if potential_icon.exists():
                    icon_path = potential_icon
                else:
                    # Try common icon names
                    for icon_name in ['icon.png', 'Icon.png', 'thumbnail.png']:
                        potential_icon = model_folder / icon_name
                        if potential_icon.exists():
                            icon_path = potential_icon
                            break
            except Exception as e:
                logger.debug(f"Could not find icon for {name}: {e}")
            
            # Load thumbnail
            thumbnail = None
            if icon_path:
                try:
                    thumbnail = QPixmap(str(icon_path))
                    if thumbnail.isNull():
                        thumbnail = None
                except Exception as e:
                    logger.debug(f"Could not load thumbnail for {name}: {e}")
            
            # Get last modified date
            last_modified = ''
            try:
                metadata = data.get('ModelSaveMetadata', {})
                last_modified = metadata.get('LastSavedDateLocalTime', '')
            except Exception as e:
                logger.debug(f"Could not get last modified date for {name}: {e}")
            
            return ModelInfo(
                name=name,
                model_id=model_id,
                folder_path=model_folder,
                vtube_json_path=vtube_json_path,
                icon_path=icon_path,
                thumbnail=thumbnail,
                hotkey_count=len(hotkeys),
                parameter_count=len(parameters),
                expression_count=expression_count,
                last_modified=last_modified
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {vtube_json_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing model info from {vtube_json_path}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _parse_item_info(self, vtube_json_path: Path, item_folder: Path) -> Optional[ItemInfo]:
        """
        Parse basic info from an item's .vtube.json file.
        
        Args:
            vtube_json_path: Path to .vtube.json file
            item_folder: Path to item folder
            
        Returns:
            ItemInfo object or None if parsing failed
        """
        import json
        
        try:
            with open(vtube_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract basic info
            name = data.get('Name', vtube_json_path.stem)
            model_id = data.get('ModelID', '')
            
            # Count hotkeys
            hotkeys = data.get('Hotkeys', [])
            
            # Find icon
            icon_path = None
            file_refs = data.get('FileReferences', {})
            icon_name = file_refs.get('Icon', 'icon.png')
            potential_icon = item_folder / icon_name
            if potential_icon.exists():
                icon_path = potential_icon
            
            # Load thumbnail
            thumbnail = None
            if icon_path:
                try:
                    thumbnail = QPixmap(str(icon_path))
                    if thumbnail.isNull():
                        thumbnail = None
                except Exception as e:
                    logger.debug(f"Could not load thumbnail for {name}: {e}")
            
            return ItemInfo(
                name=name,
                model_id=model_id,
                folder_path=item_folder,
                vtube_json_path=vtube_json_path,
                icon_path=icon_path,
                thumbnail=thumbnail,
                hotkey_count=len(hotkeys)
            )
            
        except Exception as e:
            logger.error(f"Error parsing item info from {vtube_json_path}: {e}")
            return None
    
    def get_vts_config_path(self) -> Optional[Path]:
        """
        Get path to vts_config.json (global settings).
        
        Returns:
            Path to vts_config.json or None if not found
        """
        if not self.config_path:
            return None
        
        config_file = self.config_path / "vts_config.json"
        if config_file.exists():
            return config_file
        
        return None
    
    def get_custom_params_path(self) -> Optional[Path]:
        """
        Get path to custom_parameters.json.
        
        Returns:
            Path to custom_parameters.json or None if not found
        """
        if not self.config_path:
            return None
        
        params_file = self.config_path / "custom_parameters.json"
        if params_file.exists():
            return params_file
        
        return None


# Singleton instance
_discovery_instance: Optional[VTSDiscovery] = None


def get_vts_discovery() -> VTSDiscovery:
    """
    Get or create the VTSDiscovery singleton instance.
    
    Returns:
        VTSDiscovery instance
    """
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = VTSDiscovery()
    return _discovery_instance
