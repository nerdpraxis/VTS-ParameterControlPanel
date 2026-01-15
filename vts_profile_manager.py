"""
VTS Profile Manager - Manages VTS global settings profiles
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProfileCategory(Enum):
    """Profile categories."""
    COMPLETE = "complete"
    TRACKING = "tracking"
    API = "api"
    UI = "ui"
    CUSTOM = "custom"


@dataclass
class ProfileInfo:
    """Information about a profile."""
    name: str
    file_path: Path
    category: ProfileCategory
    created_date: datetime
    vts_version: str
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "created_date": self.created_date.isoformat(),
            "vts_version": self.vts_version,
            "description": self.description,
            "tags": self.tags
        }


class VTSProfileManager:
    """Manages VTS global settings profiles."""
    
    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        Initialize the profile manager.
        
        Args:
            profiles_dir: Directory for storing profiles (defaults to ./profiles/)
        """
        if profiles_dir is None:
            profiles_dir = Path.cwd() / "profiles"
        
        self.profiles_dir = profiles_dir
        self.profiles_dir.mkdir(exist_ok=True)
        logger.info(f"VTSProfileManager initialized (profiles dir: {self.profiles_dir})")
    
    def save_profile(
        self,
        name: str,
        vts_config: Dict[str, Any],
        category: ProfileCategory = ProfileCategory.COMPLETE,
        description: str = "",
        tags: List[str] = None
    ) -> bool:
        """
        Save a VTS config as a profile.
        
        Args:
            name: Profile name
            vts_config: VTS config data (from vts_config.json)
            category: Profile category
            description: Optional description
            tags: Optional tags
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create profile data
            profile_data = {
                "profile_version": 1,
                "name": name,
                "created_date": datetime.now().isoformat(),
                "vts_version": "1.32.67",  # TODO: Extract from config
                "category": category.value,
                "description": description,
                "tags": tags or [],
                "settings": vts_config
            }
            
            # Save to file
            profile_path = self.profiles_dir / f"{name}.json"
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Saved profile: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save profile {name}: {e}")
            return False
    
    def load_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a profile.
        
        Args:
            name: Profile name
            
        Returns:
            Profile data or None if failed
        """
        try:
            profile_path = self.profiles_dir / f"{name}.json"
            if not profile_path.exists():
                logger.error(f"Profile not found: {name}")
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            logger.info(f"✓ Loaded profile: {name}")
            return profile_data
            
        except Exception as e:
            logger.error(f"Failed to load profile {name}: {e}")
            return None
    
    def list_profiles(self) -> List[ProfileInfo]:
        """
        List all available profiles.
        
        Returns:
            List of ProfileInfo objects
        """
        profiles = []
        
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                profile_info = ProfileInfo(
                    name=data.get('name', profile_file.stem),
                    file_path=profile_file,
                    category=ProfileCategory(data.get('category', 'complete')),
                    created_date=datetime.fromisoformat(data.get('created_date', datetime.now().isoformat())),
                    vts_version=data.get('vts_version', 'Unknown'),
                    description=data.get('description', ''),
                    tags=data.get('tags', [])
                )
                profiles.append(profile_info)
                
            except Exception as e:
                logger.warning(f"Error loading profile {profile_file.name}: {e}")
                continue
        
        # Sort by creation date (newest first)
        profiles.sort(key=lambda p: p.created_date, reverse=True)
        
        logger.info(f"✓ Found {len(profiles)} profiles")
        return profiles
    
    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            name: Profile name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile_path = self.profiles_dir / f"{name}.json"
            if not profile_path.exists():
                logger.error(f"Profile not found: {name}")
                return False
            
            profile_path.unlink()
            logger.info(f"✓ Deleted profile: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete profile {name}: {e}")
            return False
    
    def export_profile(self, name: str, export_path: Path) -> bool:
        """
        Export a profile to a specific location.
        
        Args:
            name: Profile name
            export_path: Path to export to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile_path = self.profiles_dir / f"{name}.json"
            if not profile_path.exists():
                logger.error(f"Profile not found: {name}")
                return False
            
            import shutil
            shutil.copy2(profile_path, export_path)
            logger.info(f"✓ Exported profile to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export profile {name}: {e}")
            return False
    
    def import_profile(self, import_path: Path) -> Optional[str]:
        """
        Import a profile from a file.
        
        Args:
            import_path: Path to profile file
            
        Returns:
            Profile name if successful, None otherwise
        """
        try:
            if not import_path.exists():
                logger.error(f"Import file not found: {import_path}")
                return None
            
            # Load and validate
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            name = data.get('name', import_path.stem)
            
            # Copy to profiles directory
            import shutil
            target_path = self.profiles_dir / f"{name}.json"
            shutil.copy2(import_path, target_path)
            
            logger.info(f"✓ Imported profile: {name}")
            return name
            
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return None
    
    def filter_settings_by_category(
        self,
        vts_config: Dict[str, Any],
        category: ProfileCategory
    ) -> Dict[str, Any]:
        """
        Filter VTS config to only include settings from a specific category.
        
        Args:
            vts_config: Full VTS config
            category: Category to filter by
            
        Returns:
            Filtered config
        """
        if category == ProfileCategory.COMPLETE:
            return vts_config
        
        # Define key patterns for each category
        category_patterns = {
            ProfileCategory.TRACKING: [
                'Config_Webcam',
                'Config_Tracking',
                'Config_LipsyncType',
                'Config_UseMicrophone',
                'Config_LastMicName'
            ],
            ProfileCategory.API: [
                'Config_API',
                'Config_StartAPI',
                'Config_Live2DAPI'
            ],
            ProfileCategory.UI: [
                'Config_FPSOption',
                'vts_main_language',
                'Config_LastBackground',
                'Config_ShowOnScreen'
            ]
        }
        
        patterns = category_patterns.get(category, [])
        if not patterns:
            return vts_config
        
        # Filter settings
        filtered_config = {
            'StringData': [],
            'IntData': [],
            'FloatData': [],
            'BoolData': []
        }
        
        for data_type in ['StringData', 'IntData', 'FloatData', 'BoolData']:
            original_data = vts_config.get(data_type, [])
            for item in original_data:
                key = item.get('Key', '')
                # Check if key matches any pattern
                if any(pattern in key for pattern in patterns):
                    filtered_config[data_type].append(item)
        
        return filtered_config
    
    def compare_profiles(
        self,
        profile1_name: str,
        profile2_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Compare two profiles and return differences.
        
        Args:
            profile1_name: First profile name
            profile2_name: Second profile name
            
        Returns:
            Dictionary with differences or None if failed
        """
        try:
            profile1 = self.load_profile(profile1_name)
            profile2 = self.load_profile(profile2_name)
            
            if not profile1 or not profile2:
                return None
            
            settings1 = profile1.get('settings', {})
            settings2 = profile2.get('settings', {})
            
            differences = {
                'only_in_profile1': [],
                'only_in_profile2': [],
                'different_values': []
            }
            
            # Compare each data type
            for data_type in ['StringData', 'IntData', 'FloatData', 'BoolData']:
                data1 = {item['Key']: item['Value'] for item in settings1.get(data_type, [])}
                data2 = {item['Key']: item['Value'] for item in settings2.get(data_type, [])}
                
                # Find keys only in profile1
                for key in data1:
                    if key not in data2:
                        differences['only_in_profile1'].append({
                            'key': key,
                            'value': data1[key],
                            'type': data_type
                        })
                    elif data1[key] != data2[key]:
                        differences['different_values'].append({
                            'key': key,
                            'profile1_value': data1[key],
                            'profile2_value': data2[key],
                            'type': data_type
                        })
                
                # Find keys only in profile2
                for key in data2:
                    if key not in data1:
                        differences['only_in_profile2'].append({
                            'key': key,
                            'value': data2[key],
                            'type': data_type
                        })
            
            return differences
            
        except Exception as e:
            logger.error(f"Failed to compare profiles: {e}")
            return None
