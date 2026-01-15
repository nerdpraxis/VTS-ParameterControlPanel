"""
VTS Backup Manager - Complete configuration backup and restore
"""

import json
import logging
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class BackupOptions:
    """Options for creating a backup."""
    include_global_config: bool = True
    include_model_configs: bool = True
    include_item_configs: bool = True
    include_custom_parameters: bool = True
    include_calibration: bool = True
    include_plugin_auth: bool = False  # Sensitive
    include_visual_effects: bool = True
    
    user_notes: str = ""
    backup_reason: str = "manual"


@dataclass
class RestoreOptions:
    """Options for restoring from backup."""
    restore_global_config: bool = True
    restore_model_configs: bool = True
    restore_item_configs: bool = True
    restore_custom_parameters: bool = True
    restore_calibration: bool = True
    restore_plugin_auth: bool = False  # Sensitive
    restore_visual_effects: bool = True
    
    create_pre_restore_backup: bool = True


@dataclass
class RestoreReport:
    """Report of restore operation."""
    success: bool
    files_restored: int = 0
    files_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    detailed_log: List[str] = field(default_factory=list)
    pre_restore_backup_path: Optional[Path] = None


class VTSBackupManager:
    """Manages complete VTS configuration backups."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize the backup manager.
        
        Args:
            backup_dir: Directory for backup storage (defaults to ./vts_backups/)
        """
        if backup_dir is None:
            backup_dir = Path.cwd() / "vts_backups"
        
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)
        logger.info(f"VTSBackupManager initialized (backup dir: {self.backup_dir})")
    
    def create_backup(
        self,
        vts_root: Path,
        output_path: Optional[Path],
        options: BackupOptions
    ) -> Optional[Path]:
        """
        Create a complete VTS configuration backup.
        
        Args:
            vts_root: VTS installation root
            output_path: Where to save the backup (None = auto-generate in backup_dir)
            options: Backup options
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            streaming_assets = vts_root / "VTube Studio_Data" / "StreamingAssets"
            if not streaming_assets.exists():
                logger.error(f"StreamingAssets not found in {vts_root}")
                return None
            
            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.backup_dir / f"vts_backup_{timestamp}.zip"
            
            logger.info(f"Creating backup: {output_path.name}")
            
            # Create backup manifest
            manifest = self._create_manifest(vts_root, options)
            
            # Create ZIP file
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add manifest
                zipf.writestr("backup_manifest.json", json.dumps(manifest, indent=2))
                
                # Add global config
                if options.include_global_config:
                    config_file = streaming_assets / "Config" / "vts_config.json"
                    if config_file.exists():
                        zipf.write(config_file, "Config/vts_config.json")
                        logger.info("  ✓ Added vts_config.json")
                
                # Add custom parameters
                if options.include_custom_parameters:
                    params_file = streaming_assets / "Config" / "custom_parameters.json"
                    if params_file.exists():
                        zipf.write(params_file, "Config/custom_parameters.json")
                        logger.info("  ✓ Added custom_parameters.json")
                
                # Add calibration files
                if options.include_calibration:
                    calibration_files = [
                        "Config/vts_lipsync_ulipsync.json",
                        "Config/webcam_calibration_mediapipe.json"
                    ]
                    for rel_path in calibration_files:
                        full_path = streaming_assets / rel_path
                        if full_path.exists():
                            zipf.write(full_path, rel_path)
                            logger.info(f"  ✓ Added {rel_path}")
                
                # Add visual effects
                if options.include_visual_effects:
                    effects_file = streaming_assets / "Effects" / "vts_saved_visual_effects.effects.json"
                    if effects_file.exists():
                        zipf.write(effects_file, "Effects/vts_saved_visual_effects.effects.json")
                        logger.info("  ✓ Added visual effects")
                
                # Add model configs
                if options.include_model_configs:
                    models_path = streaming_assets / "Live2DModels"
                    if models_path.exists():
                        count = 0
                        for model_folder in models_path.iterdir():
                            if not model_folder.is_dir():
                                continue
                            
                            # Find .vtube.json files
                            for vtube_file in model_folder.glob("*.vtube.json"):
                                # Skip backup files
                                if '.original' in vtube_file.name or '.backup' in vtube_file.name:
                                    continue
                                
                                rel_path = vtube_file.relative_to(streaming_assets)
                                zipf.write(vtube_file, str(rel_path))
                                count += 1
                        
                        logger.info(f"  ✓ Added {count} model configs")
                
                # Add item configs
                if options.include_item_configs:
                    items_path = streaming_assets / "Items"
                    if items_path.exists():
                        count = 0
                        for item_folder in items_path.iterdir():
                            if not item_folder.is_dir():
                                continue
                            
                            # Find .vtube.json files
                            for vtube_file in item_folder.glob("*.vtube.json"):
                                # Skip backup files
                                if '.original' in vtube_file.name or '.backup' in vtube_file.name:
                                    continue
                                
                                rel_path = vtube_file.relative_to(streaming_assets)
                                zipf.write(vtube_file, str(rel_path))
                                count += 1
                        
                        logger.info(f"  ✓ Added {count} item configs")
                
                # Add plugin auth (if requested)
                if options.include_plugin_auth:
                    plugins_path = streaming_assets / "Config" / "Plugins"
                    if plugins_path.exists():
                        count = 0
                        for auth_file in plugins_path.glob("*.vtsauth"):
                            rel_path = auth_file.relative_to(streaming_assets)
                            zipf.write(auth_file, str(rel_path))
                            count += 1
                        logger.info(f"  ✓ Added {count} plugin auth files")
            
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"✓ Backup created: {output_path.name} ({file_size:.2f} MB)")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def restore_backup(
        self,
        backup_path: Path,
        vts_root: Path,
        options: RestoreOptions
    ) -> RestoreReport:
        """
        Restore from a backup.
        
        Args:
            backup_path: Path to backup ZIP file
            vts_root: VTS installation root
            options: Restore options
            
        Returns:
            RestoreReport with operation details
        """
        report = RestoreReport(success=False)
        
        try:
            if not backup_path.exists():
                report.errors.append(f"Backup file not found: {backup_path}")
                return report
            
            streaming_assets = vts_root / "VTube Studio_Data" / "StreamingAssets"
            if not streaming_assets.exists():
                report.errors.append(f"StreamingAssets not found in {vts_root}")
                return report
            
            # Create pre-restore backup
            if options.create_pre_restore_backup:
                report.detailed_log.append("Creating pre-restore backup...")
                pre_backup_options = BackupOptions(
                    include_plugin_auth=False,  # Don't backup sensitive data
                    backup_reason="pre_restore"
                )
                pre_backup_path = self.create_backup(vts_root, None, pre_backup_options)
                if pre_backup_path:
                    report.pre_restore_backup_path = pre_backup_path
                    report.detailed_log.append(f"✓ Pre-restore backup: {pre_backup_path.name}")
                else:
                    report.warnings.append("Failed to create pre-restore backup")
            
            # Extract and restore
            report.detailed_log.append(f"Restoring from: {backup_path.name}")
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Read manifest
                manifest = None
                if "backup_manifest.json" in zipf.namelist():
                    manifest_data = zipf.read("backup_manifest.json")
                    manifest = json.loads(manifest_data)
                    report.detailed_log.append(f"Backup date: {manifest.get('backup_date', 'Unknown')}")
                
                # Restore files based on options
                for file_info in zipf.infolist():
                    filename = file_info.filename
                    
                    # Skip manifest
                    if filename == "backup_manifest.json":
                        continue
                    
                    # Check if should restore this file
                    should_restore = False
                    
                    if options.restore_global_config and "Config/vts_config.json" in filename:
                        should_restore = True
                    elif options.restore_custom_parameters and "Config/custom_parameters.json" in filename:
                        should_restore = True
                    elif options.restore_calibration and ("calibration" in filename.lower() or "lipsync" in filename.lower()):
                        should_restore = True
                    elif options.restore_visual_effects and "Effects/" in filename:
                        should_restore = True
                    elif options.restore_model_configs and "Live2DModels/" in filename:
                        should_restore = True
                    elif options.restore_item_configs and "Items/" in filename:
                        should_restore = True
                    elif options.restore_plugin_auth and ".vtsauth" in filename:
                        should_restore = True
                    
                    if should_restore:
                        target_path = streaming_assets / filename
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with zipf.open(filename) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                        
                        report.files_restored += 1
                        report.detailed_log.append(f"✓ Restored: {filename}")
                    else:
                        report.files_skipped += 1
            
            report.success = True
            report.detailed_log.append(f"✓ Restore complete: {report.files_restored} files restored, {report.files_skipped} skipped")
            logger.info(f"✓ Restore complete: {report.files_restored} files")
            
        except Exception as e:
            report.success = False
            report.errors.append(f"Restore failed: {e}")
            logger.error(f"Restore failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return report
    
    def validate_backup(self, backup_path: Path) -> tuple[bool, List[str]]:
        """
        Validate a backup file.
        
        Args:
            backup_path: Path to backup ZIP
            
        Returns:
            (is_valid, issues) tuple
        """
        issues = []
        
        try:
            if not backup_path.exists():
                issues.append("Backup file does not exist")
                return False, issues
            
            if not zipfile.is_zipfile(backup_path):
                issues.append("File is not a valid ZIP archive")
                return False, issues
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Check for manifest
                if "backup_manifest.json" not in zipf.namelist():
                    issues.append("Missing backup manifest")
                
                # Try to read manifest
                try:
                    manifest_data = zipf.read("backup_manifest.json")
                    manifest = json.loads(manifest_data)
                except:
                    issues.append("Failed to read backup manifest")
                
                # Check for at least some config files
                file_list = zipf.namelist()
                if not any("vts_config.json" in f for f in file_list):
                    issues.append("Warning: No vts_config.json found")
                
                # Test ZIP integrity
                bad_file = zipf.testzip()
                if bad_file:
                    issues.append(f"Corrupt file in archive: {bad_file}")
            
            is_valid = len([i for i in issues if not i.startswith("Warning")]) == 0
            return is_valid, issues
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
            return False, issues
    
    def list_backup_contents(self, backup_path: Path) -> Optional[List[str]]:
        """
        List contents of a backup.
        
        Args:
            backup_path: Path to backup ZIP
            
        Returns:
            List of filenames or None if failed
        """
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                return zipf.namelist()
        except Exception as e:
            logger.error(f"Failed to list backup contents: {e}")
            return None
    
    def _create_manifest(self, vts_root: Path, options: BackupOptions) -> Dict[str, Any]:
        """Create backup manifest with metadata."""
        return {
            "backup_version": 1,
            "backup_date": datetime.now().isoformat(),
            "vts_version": "1.32.67",  # TODO: Extract from VTS
            "vts_install_path": str(vts_root),
            "options": {
                "include_global_config": options.include_global_config,
                "include_model_configs": options.include_model_configs,
                "include_item_configs": options.include_item_configs,
                "include_custom_parameters": options.include_custom_parameters,
                "include_calibration": options.include_calibration,
                "include_plugin_auth": options.include_plugin_auth,
                "include_visual_effects": options.include_visual_effects
            },
            "user_notes": options.user_notes,
            "backup_reason": options.backup_reason
        }
