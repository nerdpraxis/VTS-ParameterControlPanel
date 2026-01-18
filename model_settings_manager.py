"""
Model Settings Manager - Manages model settings transfer operations
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from vts_file_parser import VTSFileParser, HotkeyInfo, ParameterInfo, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class TransferSettings:
    """Settings for model transfer operation."""
    
    # Bulk transfer options
    transfer_all_hotkeys: bool = False
    transfer_all_parameters: bool = False
    transfer_physics: bool = False
    transfer_position: bool = False
    transfer_name: bool = False
    transfer_folders: bool = False
    
    # Individual selection
    selected_hotkey_ids: List[str] = field(default_factory=list)
    selected_parameter_names: List[str] = field(default_factory=list)
    selected_expression_files: List[str] = field(default_factory=list)
    
    # Options
    generate_new_ids: bool = True  # Generate new UUIDs for hotkeys
    copy_expression_files: bool = True  # Copy .exp3.json and .motion3.json files
    create_backup: bool = True
    dry_run: bool = False


@dataclass
class TransferResult:
    """Result of a settings transfer operation."""
    
    success: bool
    backup_path: Optional[Path] = None
    
    # What was transferred
    hotkeys_added: int = 0
    parameters_added: int = 0
    files_copied: int = 0
    
    # Issues
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Changes summary
    changes_summary: str = ""
    detailed_log: List[str] = field(default_factory=list)
    
    # Rollback info
    can_undo: bool = False
    undo_backup_path: Optional[Path] = None
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
        logger.warning(warning)
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False
        logger.error(error)
    
    def add_log(self, message: str):
        """Add a log message."""
        self.detailed_log.append(message)
        logger.info(message)


class ModelSettingsManager:
    """Manages model settings transfer operations."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize the manager.
        
        Args:
            backup_dir: Directory for backups (defaults to ./backups/)
        """
        if backup_dir is None:
            backup_dir = Path.cwd() / "backups"
        
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)
        logger.info(f"ModelSettingsManager initialized (backup dir: {self.backup_dir})")
    
    def create_backup(self, vtube_json_path: Path, backup_type: str = "original") -> Optional[Path]:
        """
        Create a backup of a .vtube.json file.
        
        Args:
            vtube_json_path: Path to .vtube.json file to backup
            backup_type: Type of backup ("original" or "timestamped")
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not vtube_json_path.exists():
                logger.error(f"Cannot backup - file not found: {vtube_json_path}")
                return None
            
            # Determine backup filename
            if backup_type == "original":
                backup_path = vtube_json_path.with_suffix('.json.original')
            else:
                # Timestamped backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{vtube_json_path.stem}.backup_{timestamp}.json"
                backup_path = self.backup_dir / backup_name
            
            # Copy the file
            shutil.copy2(vtube_json_path, backup_path)
            logger.info(f"✓ Created backup: {backup_path.name}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_backup(self, backup_path: Path, target_path: Path) -> bool:
        """
        Restore a backup file.
        
        Args:
            backup_path: Path to backup file
            target_path: Path to restore to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            shutil.copy2(backup_path, target_path)
            logger.info(f"✓ Restored from backup: {backup_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def validate_transfer(
        self, 
        source_path: Path, 
        target_path: Path, 
        settings: TransferSettings
    ) -> ValidationResult:
        """
        Validate a transfer operation before executing.
        
        Args:
            source_path: Path to source .vtube.json
            target_path: Path to target .vtube.json
            settings: Transfer settings
            
        Returns:
            ValidationResult with any errors/warnings
        """
        result = ValidationResult(valid=True)
        
        # Check source exists
        if not source_path.exists():
            result.add_error(f"Source file not found: {source_path}")
            return result
        
        # Check target exists
        if not target_path.exists():
            result.add_error(f"Target file not found: {target_path}")
            return result
        
        # Load and validate source
        source_data = VTSFileParser.load_vtube_json(source_path)
        if not source_data:
            result.add_error("Failed to load source model config")
            return result
        
        source_validation = VTSFileParser.validate_vtube_json(source_data)
        if not source_validation.valid:
            result.add_error("Source model config is invalid")
            for error in source_validation.errors:
                result.add_error(f"  Source: {error}")
        
        # Load and validate target
        target_data = VTSFileParser.load_vtube_json(target_path)
        if not target_data:
            result.add_error("Failed to load target model config")
            return result
        
        target_validation = VTSFileParser.validate_vtube_json(target_data)
        if not target_validation.valid:
            result.add_error("Target model config is invalid")
            for error in target_validation.errors:
                result.add_error(f"  Target: {error}")
        
        # Validate file references if copying expressions
        if settings.copy_expression_files:
            source_folder = source_path.parent
            source_hotkeys = VTSFileParser.parse_hotkeys(source_data)
            
            # Filter to selected hotkeys if not transferring all
            if not settings.transfer_all_hotkeys and settings.selected_hotkey_ids:
                source_hotkeys = [
                    hk for hk in source_hotkeys 
                    if hk.hotkey_id in settings.selected_hotkey_ids
                ]
            
            file_validation = VTSFileParser.validate_file_references(source_hotkeys, source_folder)
            for warning in file_validation.warnings:
                result.add_warning(warning)
        
        return result
    
    def transfer_hotkeys(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        hotkey_ids: List[str],
        generate_new_ids: bool = True,
        target_model_folder: Optional[Path] = None
    ) -> TransferResult:
        """
        Transfer hotkeys from source to target.
        
        Only transfers hotkeys if the target model already has the required
        expression/animation files. This ensures hotkeys will work after transfer.
        
        Args:
            source_data: Source model data
            target_data: Target model data
            hotkey_ids: List of hotkey IDs to transfer
            generate_new_ids: Whether to generate new UUIDs
            target_model_folder: Path to target model folder (for checking files)
            
        Returns:
            TransferResult with operation details
        """
        result = TransferResult(success=True)
        
        source_hotkeys = source_data.get('Hotkeys', [])
        target_hotkeys = target_data.get('Hotkeys', [])
        
        # Filter source hotkeys to only selected ones
        hotkeys_to_transfer = [
            hk for hk in source_hotkeys
            if hk.get('HotkeyID') in hotkey_ids
        ]
        
        if not hotkeys_to_transfer:
            result.add_warning("No hotkeys matched the selection")
            return result
        
        # Transfer each hotkey
        skipped = []
        for hotkey in hotkeys_to_transfer:
            hotkey_name = hotkey.get('Name', 'Unknown')
            file_ref = hotkey.get('File', '')
            
            # Check if expression file exists in target model (if file is required)
            if file_ref and target_model_folder:
                target_file = target_model_folder / file_ref
                
                if not target_file.exists():
                    # Skip this hotkey - target model doesn't have the expression
                    skipped.append({
                        'name': hotkey_name,
                        'file': file_ref,
                        'action': hotkey.get('Action', '')
                    })
                    result.add_warning(
                        f"Skipped '{hotkey_name}': Target model doesn't have '{file_ref}'"
                    )
                    continue
            
            # Deep copy the hotkey data
            new_hotkey = json.loads(json.dumps(hotkey))
            
            # Generate new UUID if requested
            if generate_new_ids:
                old_id = new_hotkey['HotkeyID']
                new_id = VTSFileParser.generate_uuid()
                new_hotkey['HotkeyID'] = new_id
                result.add_log(f"✓ '{new_hotkey['Name']}': {old_id[:8]}... → {new_id[:8]}...")
            
            # Add to target
            target_hotkeys.append(new_hotkey)
            result.hotkeys_added += 1
        
        # Update target data
        target_data['Hotkeys'] = target_hotkeys
        
        # Summary
        if result.hotkeys_added > 0:
            result.add_log(f"✓ Transferred {result.hotkeys_added} hotkeys")
        
        if skipped:
            result.add_log(f"⚠ Skipped {len(skipped)} hotkeys (missing expression files)")
            for skip in skipped[:5]:  # Show first 5
                result.add_log(f"  - {skip['name']} → {skip['file']}")
            if len(skipped) > 5:
                result.add_log(f"  ... and {len(skipped) - 5} more")
        
        return result
    
    def transfer_parameters(
        self,
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        parameter_names: List[str]
    ) -> TransferResult:
        """
        Transfer parameter mappings from source to target.
        
        Args:
            source_data: Source model data
            target_data: Target model data
            parameter_names: List of parameter names to transfer
            
        Returns:
            TransferResult with operation details
        """
        result = TransferResult(success=True)
        
        source_params = source_data.get('ParameterSettings', [])
        target_params = target_data.get('ParameterSettings', [])
        
        # Filter source parameters to only selected ones
        params_to_transfer = [
            param for param in source_params
            if param.get('Name') in parameter_names
        ]
        
        if not params_to_transfer:
            result.add_warning("No parameters matched the selection")
            return result
        
        # Transfer each parameter
        for param in params_to_transfer:
            # Deep copy the parameter data
            new_param = json.loads(json.dumps(param))
            
            # Add to target
            target_params.append(new_param)
            result.parameters_added += 1
            result.add_log(f"Parameter '{new_param['Name']}': {new_param['Input']} → {new_param['OutputLive2D']}")
        
        # Update target data
        target_data['ParameterSettings'] = target_params
        
        result.add_log(f"✓ Transferred {result.parameters_added} parameters")
        return result
    
    def copy_expression_files(
        self,
        source_folder: Path,
        target_folder: Path,
        expression_files: List[str]
    ) -> TransferResult:
        """
        Copy expression and animation files from source to target.
        
        Args:
            source_folder: Source model folder
            target_folder: Target model folder
            expression_files: List of filenames to copy
            
        Returns:
            TransferResult with operation details
        """
        result = TransferResult(success=True)
        
        for filename in expression_files:
            try:
                source_file = source_folder / filename
                target_file = target_folder / filename
                
                # Create target subdirectory if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                if not source_file.exists():
                    result.add_warning(f"Source file not found: {filename}")
                    continue
                
                if target_file.exists():
                    result.add_warning(f"Target file already exists (skipping): {filename}")
                    continue
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                result.files_copied += 1
                result.add_log(f"✓ Copied: {filename}")
                
            except Exception as e:
                result.add_error(f"Failed to copy {filename}: {e}")
        
        return result
    
    def execute_transfer(
        self,
        source_path: Path,
        target_path: Path,
        settings: TransferSettings
    ) -> TransferResult:
        """
        Execute a complete transfer operation.
        
        Args:
            source_path: Path to source .vtube.json
            target_path: Path to target .vtube.json
            settings: Transfer settings
            
        Returns:
            TransferResult with operation details
        """
        result = TransferResult(success=True)
        
        try:
            # Phase 1: Validate
            result.add_log("=== Phase 1: Validation ===")
            validation = self.validate_transfer(source_path, target_path, settings)
            if not validation.valid:
                result.success = False
                for error in validation.errors:
                    result.add_error(error)
                return result
            
            for warning in validation.warnings:
                result.add_warning(warning)
            
            # Phase 2: Backup
            if settings.create_backup and not settings.dry_run:
                result.add_log("=== Phase 2: Backup ===")
                backup_path = self.create_backup(target_path, "timestamped")
                if backup_path:
                    result.backup_path = backup_path
                    result.undo_backup_path = backup_path
                    result.can_undo = True
                else:
                    result.add_error("Failed to create backup")
                    return result
            
            # Phase 3: Load data
            result.add_log("=== Phase 3: Load Data ===")
            source_data = VTSFileParser.load_vtube_json(source_path)
            target_data = VTSFileParser.load_vtube_json(target_path)
            
            if not source_data or not target_data:
                result.add_error("Failed to load model data")
                return result
            
            # Phase 4: Transfer operations
            result.add_log("=== Phase 4: Transfer ===")
            
            # Transfer hotkeys
            if settings.transfer_all_hotkeys or settings.selected_hotkey_ids:
                # Determine which hotkeys to transfer
                if settings.transfer_all_hotkeys:
                    hotkey_ids = [hk.get('HotkeyID') for hk in source_data.get('Hotkeys', [])]
                else:
                    hotkey_ids = settings.selected_hotkey_ids
                
                # Get target model folder for expression file checking
                target_model_folder = target_path.parent
                
                hotkey_result = self.transfer_hotkeys(
                    source_data,
                    target_data,
                    hotkey_ids,
                    settings.generate_new_ids,
                    target_model_folder
                )
                
                result.hotkeys_added = hotkey_result.hotkeys_added
                result.warnings.extend(hotkey_result.warnings)
                result.errors.extend(hotkey_result.errors)
                result.detailed_log.extend(hotkey_result.detailed_log)
            
            # Transfer parameters
            if settings.transfer_all_parameters or settings.selected_parameter_names:
                # Determine which parameters to transfer
                if settings.transfer_all_parameters:
                    param_names = [p.get('Name') for p in source_data.get('ParameterSettings', [])]
                else:
                    param_names = settings.selected_parameter_names
                
                param_result = self.transfer_parameters(
                    source_data,
                    target_data,
                    param_names
                )
                
                result.parameters_added = param_result.parameters_added
                result.warnings.extend(param_result.warnings)
                result.errors.extend(param_result.errors)
                result.detailed_log.extend(param_result.detailed_log)
            
            # Copy expression files
            if settings.copy_expression_files and (settings.transfer_all_hotkeys or settings.selected_hotkey_ids):
                # Collect all referenced files from transferred hotkeys
                expression_files = set()
                for hotkey in target_data.get('Hotkeys', []):
                    file = hotkey.get('File', '')
                    if file:
                        expression_files.add(file)
                
                if expression_files:
                    file_result = self.copy_expression_files(
                        source_path.parent,
                        target_path.parent,
                        list(expression_files)
                    )
                    
                    result.files_copied = file_result.files_copied
                    result.warnings.extend(file_result.warnings)
                    result.errors.extend(file_result.errors)
                    result.detailed_log.extend(file_result.detailed_log)
            
            # Phase 5: Save (if not dry run)
            if not settings.dry_run:
                result.add_log("=== Phase 5: Save ===")
                if VTSFileParser.save_vtube_json(target_path, target_data):
                    result.add_log("✓ Transfer completed successfully")
                else:
                    result.add_error("Failed to save target model config")
                    # Attempt rollback
                    if result.backup_path:
                        result.add_log("⚠ Attempting rollback...")
                        if self.restore_backup(result.backup_path, target_path):
                            result.add_log("✓ Rollback successful")
                        else:
                            result.add_error("✗ Rollback failed")
                    return result
            else:
                result.add_log("=== Dry Run Complete (no changes made) ===")
            
            # Create summary
            summary_parts = []
            if result.hotkeys_added > 0:
                summary_parts.append(f"{result.hotkeys_added} hotkeys")
            if result.parameters_added > 0:
                summary_parts.append(f"{result.parameters_added} parameters")
            if result.files_copied > 0:
                summary_parts.append(f"{result.files_copied} files")
            
            if summary_parts:
                result.changes_summary = f"Transferred: {', '.join(summary_parts)}"
            else:
                result.changes_summary = "No changes made"
            
            return result
            
        except Exception as e:
            result.success = False
            result.add_error(f"Unexpected error during transfer: {e}")
            logger.exception("Transfer exception:")
            return result
