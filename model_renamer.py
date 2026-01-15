"""
Model Renamer - Properly rename/duplicate VTS models
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from vts_file_parser import VTSFileParser

logger = logging.getLogger(__name__)


@dataclass
class RenameResult:
    """Result of rename operation."""
    success: bool
    old_path: Optional[Path] = None
    new_path: Optional[Path] = None
    error: Optional[str] = None
    backup_path: Optional[Path] = None
    changes_made: list = None
    
    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []


class ModelRenamer:
    """Handles proper model renaming and duplication."""
    
    def __init__(self):
        self.parser = VTSFileParser()
        logger.info("ModelRenamer initialized")
    
    def rename_model(
        self,
        model_folder: Path,
        new_name: str,
        create_new_id: bool = True
    ) -> RenameResult:
        """
        Properly rename a model.
        
        Args:
            model_folder: Path to the model folder
            new_name: New model name
            create_new_id: Whether to generate a new ModelID
            
        Returns:
            RenameResult with operation details
        """
        result = RenameResult(success=False)
        result.old_path = model_folder
        
        try:
            if not model_folder.exists():
                result.error = f"Model folder not found: {model_folder}"
                return result
            
            # Find .vtube.json file
            vtube_files = list(model_folder.glob("*.vtube.json"))
            # Filter out backups
            vtube_files = [f for f in vtube_files 
                          if '.original' not in f.name 
                          and '.backup' not in f.name
                          and ' - Kopie' not in f.name]
            
            if not vtube_files:
                result.error = "No .vtube.json file found in model folder"
                return result
            
            if len(vtube_files) > 1:
                result.error = f"Multiple .vtube.json files found: {[f.name for f in vtube_files]}"
                return result
            
            old_vtube_file = vtube_files[0]
            logger.info(f"Found .vtube.json: {old_vtube_file.name}")
            
            # Create backup
            backup_path = self._create_backup(model_folder, old_vtube_file)
            result.backup_path = backup_path
            result.changes_made.append(f"Created backup: {backup_path.name}")
            
            # Load current config
            config = self.parser.load_vtube_json(old_vtube_file)
            if not config:
                result.error = f"Failed to load .vtube.json: {old_vtube_file}"
                return result
            
            # Update Name field
            old_model_name = config.get('Name', 'Unknown')
            config['Name'] = new_name
            result.changes_made.append(f"Updated Name: '{old_model_name}' → '{new_name}'")
            logger.info(f"Updated Name field: {old_model_name} → {new_name}")
            
            # Generate new ModelID if requested
            if create_new_id:
                old_model_id = config.get('ModelID', '')
                new_model_id = self.parser.generate_uuid()
                config['ModelID'] = new_model_id
                result.changes_made.append(f"Generated new ModelID: {new_model_id[:8]}...")
                logger.info(f"Generated new ModelID: {old_model_id[:8]}... → {new_model_id[:8]}...")
            
            # Save updated config to new filename
            new_vtube_filename = f"{new_name}.vtube.json"
            new_vtube_path = model_folder / new_vtube_filename
            
            if new_vtube_path.exists() and new_vtube_path != old_vtube_file:
                result.error = f"File already exists: {new_vtube_filename}"
                return result
            
            # Write updated config
            with open(new_vtube_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            result.changes_made.append(f"Created new .vtube.json: {new_vtube_filename}")
            logger.info(f"Saved new .vtube.json: {new_vtube_path.name}")
            
            # Delete old .vtube.json if different filename
            if old_vtube_file != new_vtube_path:
                old_vtube_file.unlink()
                result.changes_made.append(f"Removed old .vtube.json: {old_vtube_file.name}")
                logger.info(f"Deleted old .vtube.json: {old_vtube_file.name}")
            
            # Rename folder
            new_folder_path = model_folder.parent / new_name
            
            if new_folder_path.exists() and new_folder_path != model_folder:
                result.error = f"Folder already exists: {new_name}"
                # Restore old file
                if old_vtube_file != new_vtube_path:
                    new_vtube_path.unlink()
                    with open(old_vtube_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                return result
            
            if model_folder != new_folder_path:
                model_folder.rename(new_folder_path)
                result.changes_made.append(f"Renamed folder: '{model_folder.name}' → '{new_name}'")
                logger.info(f"Renamed folder: {model_folder.name} → {new_name}")
                result.new_path = new_folder_path
            else:
                result.new_path = model_folder
            
            result.success = True
            logger.info(f"✓ Model renamed successfully: {model_folder.name} → {new_name}")
            return result
            
        except Exception as e:
            result.error = f"Rename failed: {e}"
            logger.error(f"Rename failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return result
    
    def _create_backup(self, model_folder: Path, vtube_file: Path) -> Optional[Path]:
        """Create a backup of the .vtube.json file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{vtube_file.stem}.backup_{timestamp}.json"
            backup_path = model_folder / backup_name
            
            shutil.copy2(vtube_file, backup_path)
            logger.info(f"Created backup: {backup_name}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def validate_rename(
        self,
        model_folder: Path,
        new_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if rename is possible.
        
        Args:
            model_folder: Model folder path
            new_name: Proposed new name
            
        Returns:
            (is_valid, error_message) tuple
        """
        # Check folder exists
        if not model_folder.exists():
            return False, "Model folder not found"
        
        # Check for .vtube.json
        vtube_files = list(model_folder.glob("*.vtube.json"))
        vtube_files = [f for f in vtube_files 
                      if '.original' not in f.name 
                      and '.backup' not in f.name
                      and ' - Kopie' not in f.name]
        
        if not vtube_files:
            return False, "No .vtube.json file found"
        
        if len(vtube_files) > 1:
            return False, f"Multiple .vtube.json files found"
        
        # Check new name is valid
        if not new_name or not new_name.strip():
            return False, "New name cannot be empty"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in new_name for char in invalid_chars):
            return False, f"Name contains invalid characters: {' '.join(invalid_chars)}"
        
        # Check if target folder/file already exists
        new_folder_path = model_folder.parent / new_name
        if new_folder_path.exists() and new_folder_path != model_folder:
            return False, f"A model folder named '{new_name}' already exists"
        
        return True, None
