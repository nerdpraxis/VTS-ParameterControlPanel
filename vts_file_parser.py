"""
VTS File Parser - Parses and validates VTube Studio .vtube.json files
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HotkeyAction(Enum):
    """Hotkey action types."""
    TOGGLE_EXPRESSION = "ToggleExpression"
    TRIGGER_ANIMATION = "TriggerAnimation"
    CHANGE_IDLE_ANIMATION = "ChangeIdleAnimation"
    REMOVE_ALL_EXPRESSIONS = "RemoveAllExpressions"


@dataclass
class ValidationResult:
    """Result of validation check."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def has_issues(self) -> bool:
        """Check if there are any errors or warnings."""
        return len(self.errors) > 0 or len(self.warnings) > 0


@dataclass
class HotkeyInfo:
    """Parsed hotkey information."""
    hotkey_id: str
    name: str
    action: str
    file: str
    folder: str
    is_global: bool
    is_active: bool
    triggers: Dict[str, Any]
    
    # Full hotkey data (for transfer)
    raw_data: Dict[str, Any]
    
    def get_keybind_string(self) -> str:
        """Get human-readable keybind string."""
        triggers = self.triggers
        parts = []
        
        if triggers.get('Trigger1'):
            parts.append(triggers['Trigger1'])
        if triggers.get('Trigger2'):
            parts.append(triggers['Trigger2'])
        if triggers.get('Trigger3'):
            parts.append(triggers['Trigger3'])
        
        if parts:
            return " + ".join(parts)
        
        screen_btn = triggers.get('ScreenButton', -1)
        if screen_btn >= 0:
            return f"Screen Button {screen_btn}"
        
        return "No keybind"


@dataclass
class ParameterInfo:
    """Parsed parameter mapping information."""
    name: str
    input_param: str
    output_param: str
    folder: str
    smoothing: int
    input_range: Tuple[float, float]
    output_range: Tuple[float, float]
    
    # Full parameter data (for transfer)
    raw_data: Dict[str, Any]


class VTSFileParser:
    """Parser and validator for VTube Studio .vtube.json files."""
    
    @staticmethod
    def load_vtube_json(path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a .vtube.json file.
        
        Args:
            path: Path to .vtube.json file
            
        Returns:
            Parsed JSON data or None if failed
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"✓ Loaded {path.name}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {path.name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading {path.name}: {e}")
            return None
    
    @staticmethod
    def save_vtube_json(path: Path, data: Dict[str, Any]) -> bool:
        """
        Save a .vtube.json file.
        
        Args:
            path: Path to save to
            data: JSON data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate before saving
            validation = VTSFileParser.validate_vtube_json(data)
            if not validation.valid:
                logger.error(f"Validation failed before save: {validation.errors}")
                return False
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved {path.name}")
            return True
        except Exception as e:
            logger.error(f"Error saving {path.name}: {e}")
            return False
    
    @staticmethod
    def validate_vtube_json(data: Dict[str, Any]) -> ValidationResult:
        """
        Validate .vtube.json structure.
        
        Args:
            data: JSON data to validate
            
        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(valid=True)
        
        # Check required top-level fields
        required_fields = ['Version', 'Name', 'ModelID']
        for field in required_fields:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        # Validate ModelID format (32 hex chars, no dashes)
        model_id = data.get('ModelID', '')
        if not VTSFileParser.validate_uuid(model_id):
            result.add_error(f"Invalid ModelID format: {model_id}")
        
        # Validate hotkeys
        hotkeys = data.get('Hotkeys', [])
        if not isinstance(hotkeys, list):
            result.add_error("Hotkeys must be a list")
        else:
            for i, hotkey in enumerate(hotkeys):
                hotkey_issues = VTSFileParser._validate_hotkey(hotkey)
                for error in hotkey_issues:
                    result.add_warning(f"Hotkey {i} ({hotkey.get('Name', 'unnamed')}): {error}")
        
        # Validate parameter settings
        params = data.get('ParameterSettings', [])
        if not isinstance(params, list):
            result.add_error("ParameterSettings must be a list")
        
        # Check file references
        file_refs = data.get('FileReferences', {})
        if not isinstance(file_refs, dict):
            result.add_warning("FileReferences should be a dict")
        
        return result
    
    @staticmethod
    def _validate_hotkey(hotkey: Dict[str, Any]) -> List[str]:
        """Validate a single hotkey entry."""
        issues = []
        
        # Check required fields
        if 'HotkeyID' not in hotkey:
            issues.append("Missing HotkeyID")
        elif not VTSFileParser.validate_uuid(hotkey['HotkeyID']):
            issues.append(f"Invalid HotkeyID format: {hotkey['HotkeyID']}")
        
        if 'Name' not in hotkey:
            issues.append("Missing Name")
        
        if 'Action' not in hotkey:
            issues.append("Missing Action")
        
        # Validate action type
        action = hotkey.get('Action', '')
        valid_actions = [a.value for a in HotkeyAction]
        if action and action not in valid_actions:
            issues.append(f"Unknown action: {action}")
        
        return issues
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """
        Validate UUID format (32 hex chars, no dashes).
        
        Args:
            uuid_str: UUID string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not uuid_str:
            return False
        
        # VTS uses 32 hex chars, lowercase, no dashes
        pattern = r'^[a-f0-9]{32}$'
        return bool(re.match(pattern, uuid_str))
    
    @staticmethod
    def generate_uuid() -> str:
        """
        Generate a new UUID in VTS format (32 hex chars, no dashes).
        
        Returns:
            New UUID string
        """
        import uuid
        new_uuid = uuid.uuid4().hex
        return new_uuid.lower()
    
    @staticmethod
    def parse_hotkeys(data: Dict[str, Any]) -> List[HotkeyInfo]:
        """
        Parse hotkeys from .vtube.json data.
        
        Args:
            data: Parsed .vtube.json data
            
        Returns:
            List of HotkeyInfo objects
        """
        hotkeys = []
        
        for hotkey_data in data.get('Hotkeys', []):
            try:
                hotkey_info = HotkeyInfo(
                    hotkey_id=hotkey_data.get('HotkeyID', ''),
                    name=hotkey_data.get('Name', ''),
                    action=hotkey_data.get('Action', ''),
                    file=hotkey_data.get('File', ''),
                    folder=hotkey_data.get('Folder', ''),
                    is_global=hotkey_data.get('IsGlobal', False),
                    is_active=hotkey_data.get('IsActive', True),
                    triggers=hotkey_data.get('Triggers', {}),
                    raw_data=hotkey_data
                )
                hotkeys.append(hotkey_info)
            except Exception as e:
                logger.warning(f"Error parsing hotkey: {e}")
                continue
        
        return hotkeys
    
    @staticmethod
    def parse_parameters(data: Dict[str, Any]) -> List[ParameterInfo]:
        """
        Parse parameter mappings from .vtube.json data.
        
        Args:
            data: Parsed .vtube.json data
            
        Returns:
            List of ParameterInfo objects
        """
        parameters = []
        
        for param_data in data.get('ParameterSettings', []):
            try:
                param_info = ParameterInfo(
                    name=param_data.get('Name', ''),
                    input_param=param_data.get('Input', ''),
                    output_param=param_data.get('OutputLive2D', ''),
                    folder=param_data.get('Folder', ''),
                    smoothing=param_data.get('Smoothing', 0),
                    input_range=(
                        param_data.get('InputRangeLower', 0.0),
                        param_data.get('InputRangeUpper', 1.0)
                    ),
                    output_range=(
                        param_data.get('OutputRangeLower', 0.0),
                        param_data.get('OutputRangeUpper', 1.0)
                    ),
                    raw_data=param_data
                )
                parameters.append(param_info)
            except Exception as e:
                logger.warning(f"Error parsing parameter: {e}")
                continue
        
        return parameters
    
    @staticmethod
    def get_expression_files(model_folder: Path) -> List[str]:
        """
        Get list of expression files in a model folder.
        
        Args:
            model_folder: Path to model folder
            
        Returns:
            List of expression filenames
        """
        expressions = []
        
        # Find all .exp3.json files
        for exp_file in model_folder.glob("*.exp3.json"):
            expressions.append(exp_file.name)
        
        # Also check Expressions subfolder if it exists
        exp_folder = model_folder / "Expressions"
        if exp_folder.exists():
            for exp_file in exp_folder.glob("*.exp3.json"):
                expressions.append(f"Expressions/{exp_file.name}")
        
        return sorted(expressions)
    
    @staticmethod
    def get_animation_files(model_folder: Path) -> List[str]:
        """
        Get list of animation files in a model folder.
        
        Args:
            model_folder: Path to model folder
            
        Returns:
            List of animation filenames
        """
        animations = []
        
        # Find all .motion3.json files
        for anim_file in model_folder.glob("*.motion3.json"):
            animations.append(anim_file.name)
        
        # Also check Animations subfolder if it exists
        anim_folder = model_folder / "Animations"
        if anim_folder.exists():
            for anim_file in anim_folder.glob("*.motion3.json"):
                animations.append(f"Animations/{anim_file.name}")
        
        return sorted(animations)
    
    @staticmethod
    def validate_file_references(hotkeys: List[HotkeyInfo], model_folder: Path) -> ValidationResult:
        """
        Validate that all hotkey file references exist.
        
        Args:
            hotkeys: List of hotkeys to validate
            model_folder: Path to model folder
            
        Returns:
            ValidationResult with any missing file warnings
        """
        result = ValidationResult(valid=True)
        
        for hotkey in hotkeys:
            if not hotkey.file:
                continue
            
            # Check if file exists
            file_path = model_folder / hotkey.file
            if not file_path.exists():
                # Check in subfolders
                alt_path = model_folder / "Expressions" / hotkey.file
                if not alt_path.exists():
                    result.add_warning(f"Hotkey '{hotkey.name}': File not found: {hotkey.file}")
        
        return result
