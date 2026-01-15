# VTS Model Settings Manager - Comprehensive Implementation Plan

**Created:** 2026-01-15  
**Target App:** vts-control-panel (standalone fork)  
**Purpose:** Add comprehensive model settings backup, transfer, and profile management

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Feature Overview](#feature-overview)
3. [Technical Architecture](#technical-architecture)
4. [Implementation Phases](#implementation-phases)
5. [UI/UX Design](#uiux-design)
6. [Data Structures](#data-structures)
7. [Safety & Validation](#safety--validation)
8. [File Structure](#file-structure)
9. [Testing Strategy](#testing-strategy)
10. [Future Enhancements](#future-enhancements)

---

## 1. Executive Summary

### Goal
Create a comprehensive VTS Model Settings Manager that allows users to:
- Backup and restore complete model configurations
- Transfer specific settings between models (hotkeys, parameters, etc.)
- Create and manage VTS settings profiles
- Generate full configuration backups as ZIP files
- All operations with automatic safety backups

### Key Benefits
- **Safety First**: Automatic backup creation before any modifications
- **Granular Control**: Choose exactly what to transfer (specific hotkeys, parameters, etc.)
- **Profile System**: Save and load different VTS global settings configurations
- **Disaster Recovery**: Complete configuration backup/restore to ZIP
- **User-Friendly**: Visual thumbnail display, name editing, intuitive UI

### Success Criteria
- ✅ Zero risk of data loss (automatic "original" backups)
- ✅ Can copy settings between any two models
- ✅ Can selectively transfer individual hotkeys/parameters/expressions
- ✅ Can create and restore complete system backups
- ✅ Intuitive UI with thumbnails and clear labeling
- ✅ Comprehensive error handling and validation

---

## 2. Feature Overview

### 2.1 Model Settings Transfer

**Core Functionality:**
- Discover all installed VTS models
- Display model thumbnails, names, and metadata
- Select source and target models
- Choose which settings to transfer:
  - ✅ All hotkeys (bulk)
  - ✅ Specific hotkeys (individual selection)
  - ✅ All parameter mappings (bulk)
  - ✅ Specific parameter mappings (individual selection)
  - ✅ All expressions (referenced files)
  - ✅ Specific expressions (individual selection)
  - ✅ Physics settings
  - ✅ Position/rotation/scale
  - ✅ Model name and display name
  - ✅ Saved active expressions
  - ✅ Hotkey folders organization

**Safety Features:**
- Automatic `.vtube.json.original` backup before any modification
- Validation of transferred settings (parameter existence, file references)
- Dry-run preview mode (shows what will change without applying)
- Undo/rollback support (restore from .original backup)

### 2.2 Global VTS Settings Profiles

**Core Functionality:**
- Save current `vts_config.json` as named profile
- Load saved profiles
- Compare profiles (diff view)
- Manage profile library (rename, delete, export)
- Profile categories:
  - ✅ Complete profile (all 1174 settings)
  - ✅ Tracking profile (webcam, tracking quality, lipsync)
  - ✅ API profile (port, token, remote settings)
  - ✅ UI profile (language, FPS, window settings)
  - ✅ Custom profile (user-selected settings)

**Use Cases:**
- Switch between "streaming" and "recording" setups
- Share tracking configurations with other VTubers
- Test different settings without losing current config
- Quick reset to known-good configuration

### 2.3 Complete Configuration Backup

**Core Functionality:**
- Create ZIP archive of all VTS configuration files
- User-selectable backup location
- Backup includes:
  - ✅ `vts_config.json`
  - ✅ All `.vtube.json` files (models + items)
  - ✅ `custom_parameters.json`
  - ✅ Calibration files
  - ✅ Plugin auth files (`.vtsauth`) - with security warning
  - ✅ Visual effects settings
  - ✅ Metadata (backup date, VTS version, user notes)
- Restore from ZIP with validation
- Selective restore (choose which files to restore)

**Safety Features:**
- Pre-restore backup of current config
- Validation of ZIP contents before restore
- Confirmation dialogs with clear explanations
- Restore log/report showing what was changed

---

## 3. Technical Architecture

### 3.1 New Components

```
vts-control-panel/
├── main.py                         (existing)
├── vts_model_manager_tab.py        ← NEW TAB
├── model_settings_manager.py       ← Core logic for model operations
├── vts_profile_manager.py          ← Profile management logic
├── vts_backup_manager.py           ← Backup/restore logic
├── vts_file_parser.py              ← .vtube.json parsing and validation
├── vts_discovery.py                ← VTS installation discovery
├── ui/
│   ├── model_selector_widget.py    ← Model selection UI
│   ├── settings_transfer_widget.py ← Transfer configuration UI
│   ├── profile_manager_widget.py   ← Profile management UI
│   └── backup_restore_widget.py    ← Backup/restore UI
└── data/
    ├── profiles/                   ← Saved VTS profiles
    ├── backups/                    ← Local backup storage
    └── temp/                       ← Temporary extraction/validation
```

### 3.2 Key Classes

#### `VTSDiscovery`
```python
class VTSDiscovery:
    """Discovers VTS installation and models."""
    
    def find_vts_installation() -> Optional[Path]
    def get_models_list() -> List[ModelInfo]
    def get_items_list() -> List[ItemInfo]
    def get_vts_config_path() -> Path
```

#### `ModelInfo`
```python
@dataclass
class ModelInfo:
    name: str
    model_id: str
    folder_path: Path
    vtube_json_path: Path
    icon_path: Optional[Path]
    thumbnail: Optional[QPixmap]
    hotkey_count: int
    parameter_count: int
    expression_count: int
```

#### `ModelSettingsManager`
```python
class ModelSettingsManager:
    """Manages model settings transfer operations."""
    
    def load_model_config(path: Path) -> Dict
    def backup_model_config(path: Path) -> Path
    def validate_transfer(source: Dict, target: Dict, settings: TransferSettings) -> ValidationResult
    def transfer_hotkeys(source: Dict, target: Dict, hotkey_ids: List[str]) -> Dict
    def transfer_parameters(source: Dict, target: Dict, param_names: List[str]) -> Dict
    def transfer_expressions(source: Path, target: Path, expr_files: List[str]) -> None
    def save_model_config(path: Path, config: Dict) -> None
```

#### `TransferSettings`
```python
@dataclass
class TransferSettings:
    transfer_all_hotkeys: bool = False
    selected_hotkey_ids: List[str] = field(default_factory=list)
    transfer_all_parameters: bool = False
    selected_parameter_names: List[str] = field(default_factory=list)
    transfer_physics: bool = False
    transfer_position: bool = False
    transfer_name: bool = False
    transfer_expressions: bool = False
    selected_expression_files: List[str] = field(default_factory=list)
    transfer_folders: bool = False
    generate_new_ids: bool = True  # Generate new UUIDs for hotkeys
    create_backup: bool = True
    dry_run: bool = False
```

#### `VTSProfileManager`
```python
class VTSProfileManager:
    """Manages VTS global settings profiles."""
    
    def save_profile(name: str, config: Dict, category: ProfileCategory) -> None
    def load_profile(name: str) -> Dict
    def list_profiles() -> List[ProfileInfo]
    def compare_profiles(profile1: str, profile2: str) -> DiffResult
    def delete_profile(name: str) -> None
    def export_profile(name: str, export_path: Path) -> None
    def import_profile(import_path: Path) -> None
```

#### `VTSBackupManager`
```python
class VTSBackupManager:
    """Manages complete VTS configuration backups."""
    
    def create_backup(output_path: Path, options: BackupOptions) -> None
    def restore_backup(zip_path: Path, options: RestoreOptions) -> RestoreReport
    def validate_backup(zip_path: Path) -> ValidationResult
    def list_backup_contents(zip_path: Path) -> List[str]
```

---

## 4. Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goals:**
- VTS installation discovery
- `.vtube.json` parsing and validation
- Basic model info display

**Tasks:**
1. Create `VTSDiscovery` class
   - Detect VTS StreamingAssets folder
   - Scan Live2DModels folder
   - Parse model names, IDs, metadata
   - Load model thumbnails

2. Create `VTSFileParser` class
   - Parse `.vtube.json` files
   - Validate JSON structure
   - Extract hotkeys, parameters, expressions
   - Validate UUID formats, file references

3. Create `ModelInfo` dataclass
   - Store all model metadata
   - Load and cache thumbnails
   - Count hotkeys, parameters, expressions

4. Create basic UI framework
   - Add new tab to main window
   - Create placeholder widgets
   - Test VTS discovery and model listing

**Deliverable:** Can discover and display all installed VTS models with basic info.

---

### Phase 2: Model Settings Transfer (Week 2-3)

**Goals:**
- Transfer hotkeys between models
- Transfer parameter mappings
- Transfer expressions and files
- Automatic backup creation

**Tasks:**
1. Create `ModelSettingsManager` class
   - Implement backup creation (`.vtube.json.original`)
   - Implement hotkey transfer logic
   - Implement parameter transfer logic
   - Handle UUID regeneration

2. Create `ModelSelectorWidget`
   - Source model dropdown/list
   - Target model dropdown/list
   - Display thumbnails and names
   - Show model stats (hotkey count, etc.)

3. Create `SettingsTransferWidget`
   - Checkboxes for bulk transfer options
   - Tree/list view for individual selection
   - Hotkey list with name, keybind, action
   - Parameter list with name, input, output
   - Expression file list

4. Implement transfer validation
   - Check target model has required parameters
   - Validate expression files exist
   - Check for UUID conflicts
   - Show warnings/errors before transfer

5. Implement safe transfer operation
   - Create backup before modification
   - Apply transfers
   - Validate result
   - Provide rollback option

**Deliverable:** Can transfer hotkeys, parameters, and expressions between any two models safely.

---

### Phase 3: Expression & File Transfer (Week 3-4)

**Goals:**
- Copy `.exp3.json` and `.motion3.json` files
- Handle expression dependencies
- Update file references in hotkeys

**Tasks:**
1. Implement expression file copying
   - Detect referenced expression files in hotkeys
   - Copy `.exp3.json` files to target model folder
   - Copy `.motion3.json` files to target model folder
   - Handle filename conflicts (rename, skip, overwrite)

2. Implement file reference updating
   - Update `File` field in transferred hotkeys
   - Update `IdleAnimation` references if transferred
   - Validate all file paths after transfer

3. Add expression selection UI
   - Show all expressions in source model
   - Display expression type (ToggleExpression, TriggerAnimation)
   - Show which hotkeys use each expression
   - Allow individual expression selection

4. Add preview/dry-run mode
   - Show what will be transferred
   - Show what files will be copied
   - Show resulting configuration (without applying)
   - Allow user to review and confirm

**Deliverable:** Can fully transfer hotkeys with all associated expression files.

---

### Phase 4: VTS Settings Profiles (Week 4-5)

**Goals:**
- Save/load VTS global settings profiles
- Profile categories (tracking, API, UI, custom)
- Profile comparison and management

**Tasks:**
1. Create `VTSProfileManager` class
   - Save `vts_config.json` as named profile
   - Load profile and apply to VTS config
   - List all saved profiles
   - Delete/rename profiles

2. Create `ProfileManagerWidget`
   - List view of all profiles
   - Save current settings as new profile
   - Load profile button (with confirmation)
   - Delete profile button
   - Profile metadata display (date created, VTS version)

3. Implement profile categories
   - Complete profile (all settings)
   - Tracking profile (webcam, tracking, lipsync only)
   - API profile (port, token, remote settings only)
   - UI profile (language, FPS, window settings only)
   - Custom profile (user selects settings categories)

4. Implement profile comparison
   - Compare two profiles (diff view)
   - Highlight differences
   - Show only changed settings
   - Export comparison report

5. Add profile import/export
   - Export profile as JSON file
   - Import profile from JSON file
   - Share profiles with other users

**Deliverable:** Complete profile management system for VTS global settings.

---

### Phase 5: Complete Backup & Restore (Week 5-6)

**Goals:**
- Create ZIP backups of entire VTS configuration
- Restore from ZIP backups
- Selective restore options
- Metadata and logging

**Tasks:**
1. Create `VTSBackupManager` class
   - Create ZIP archive of all config files
   - Include metadata (date, VTS version, user notes)
   - Validate ZIP contents before creation
   - User-selectable backup location

2. Implement backup file selection
   - Checkbox tree for file selection:
     - Global settings (`vts_config.json`)
     - All model configs (bulk)
     - Individual model configs (selective)
     - All item configs (bulk)
     - Custom parameters
     - Calibration files
     - Plugin auth files (with warning)
     - Visual effects settings

3. Create `BackupRestoreWidget`
   - "Create Backup" section:
     - File selection tree
     - Backup location picker
     - User notes text field
     - Progress bar during backup
   - "Restore Backup" section:
     - Select ZIP file button
     - Preview backup contents
     - Selective restore options
     - Progress bar during restore

4. Implement restore validation
   - Validate ZIP structure
   - Check VTS version compatibility
   - Show list of files to be restored
   - Create pre-restore backup of current config
   - Confirmation dialog with clear explanation

5. Implement restore operation
   - Extract ZIP to temp location
   - Validate each file
   - Copy files to VTS config locations
   - Generate restore report
   - Show success/failure for each file

6. Add restore logging
   - Log all restore operations
   - Record which files were restored
   - Record any errors/warnings
   - Save restore report to file

**Deliverable:** Complete backup/restore system with ZIP archives.

---

### Phase 6: Polish & Safety Features (Week 6-7)

**Goals:**
- Enhanced validation
- Better error handling
- User guidance and tooltips
- Documentation

**Tasks:**
1. Enhance validation
   - Validate UUID formats (32 hex chars, no dashes)
   - Validate parameter name formats
   - Check for circular dependencies
   - Validate file paths and references
   - Check for conflicting settings

2. Add comprehensive error handling
   - Graceful failure handling
   - Detailed error messages
   - Rollback on failure
   - User-friendly error dialogs

3. Add user guidance
   - Tooltips on all controls
   - Info dialogs explaining operations
   - Warning dialogs for risky operations
   - Help text for each feature

4. Add confirmation dialogs
   - "Are you sure?" for destructive operations
   - Preview of changes before applying
   - Explanation of what will happen
   - Option to create backup first

5. Create documentation
   - User guide for each feature
   - Safety best practices
   - Troubleshooting guide
   - Example workflows

6. Add visual feedback
   - Progress bars for long operations
   - Status messages during operations
   - Success/failure notifications
   - Icons and visual indicators

**Deliverable:** Polished, production-ready feature with comprehensive safety.

---

## 5. UI/UX Design

### 5.1 New Tab: "Model Manager"

**Layout Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Model Manager                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📁 Model Settings Transfer                          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  Source Model:  [Dropdown ▼] [Thumbnail] [Info]    │   │
│  │  Target Model:  [Dropdown ▼] [Thumbnail] [Info]    │   │
│  │                                                     │   │
│  │  Transfer Options:                                  │   │
│  │  ☐ All Hotkeys          ☐ All Parameters          │   │
│  │  ☐ All Expressions      ☐ Physics Settings         │   │
│  │  ☐ Model Position       ☐ Model Name              │   │
│  │                                                     │   │
│  │  Or select specific items:                          │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ Hotkeys:  [Tree view with checkboxes]      │   │   │
│  │  │  ☐ Smile (Alt+Ctrl+1) - ToggleExpression  │   │   │
│  │  │  ☐ Wink (Alt+Ctrl+2) - ToggleExpression   │   │   │
│  │  │  ☐ Wave (Alt+Ctrl+3) - TriggerAnimation   │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │  [Preview Transfer] [Transfer Settings →]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 💾 VTS Settings Profiles                            │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  Saved Profiles:                                    │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │ • Streaming Setup     (2026-01-15)         │   │   │
│  │  │ • Recording Setup     (2026-01-10)         │   │   │
│  │  │ • Test Configuration  (2026-01-08)         │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │  [Save Current] [Load] [Compare] [Delete]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📦 Complete Configuration Backup                    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  [Create Backup ZIP...] [Restore from ZIP...]      │   │
│  │                                                     │   │
│  │  Last Backup: 2026-01-15 14:30                     │   │
│  │  Location: D:\VTS_Backups\backup_20260115.zip      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Model Selector Widget

**Design:**
```
┌─────────────────────────────────────────────────────────┐
│ Select Model:                                           │
├─────────────────────────────────────────────────────────┤
│  [Dropdown: Aika_Chibi_4 ▼]                            │
│                                                         │
│  ┌──────────┐                                          │
│  │          │  Name: Aika_Chibi_4                      │
│  │ [Thumb]  │  ID: 7f4cb247da49...                     │
│  │          │  Hotkeys: 36                             │
│  │          │  Parameters: 124                         │
│  └──────────┘  Expressions: 18                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Dropdown shows all models with thumbnails
- Large thumbnail display for selected model
- Model metadata (ID, counts, path)
- Quick validation indicators (✓ valid config, ⚠ warnings)

### 5.3 Settings Transfer Dialog

**Design:**
```
┌──────────────────────────────────────────────────────────────┐
│ Transfer Settings: Aika_Chibi_4 → Aika_2_1                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Bulk Transfer Options:                                      │
│  ┌────────────────────┐  ┌────────────────────┐            │
│  │ ☑ All Hotkeys      │  │ ☐ All Parameters   │            │
│  │   (36 hotkeys)     │  │   (124 parameters) │            │
│  └────────────────────┘  └────────────────────┘            │
│                                                              │
│  Individual Selection:                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Hotkeys:                                    [Search] │   │
│  │ ┌────────────────────────────────────────────────┐  │   │
│  │ │ ☑ Smile (Alt+Ctrl+1)                           │  │   │
│  │ │   Action: ToggleExpression                     │  │   │
│  │ │   File: Smile.exp3.json ✓                      │  │   │
│  │ │                                                 │  │   │
│  │ │ ☑ Wink (Alt+Ctrl+2)                            │  │   │
│  │ │   Action: ToggleExpression                     │  │   │
│  │ │   File: Wink.exp3.json ✓                       │  │   │
│  │ │                                                 │  │   │
│  │ │ ☐ Wave (Alt+Ctrl+3)                            │  │   │
│  │ │   Action: TriggerAnimation                     │  │   │
│  │ │   File: Wave.motion3.json ⚠ (not in target)   │  │   │
│  │ └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Options:                                                    │
│  ☑ Create backup before transfer                            │
│  ☑ Copy expression files to target                          │
│  ☑ Generate new hotkey IDs                                  │
│  ☐ Dry run (preview only)                                   │
│                                                              │
│  [Preview Changes]  [Cancel]  [Transfer →]                  │
└──────────────────────────────────────────────────────────────┘
```

**Features:**
- Bulk selection for common operations
- Individual item selection with validation indicators
- File validation (✓ exists, ⚠ missing, ⓘ will be copied)
- Safety options clearly visible
- Preview button to see changes before applying

### 5.4 Transfer Preview Dialog

**Design:**
```
┌──────────────────────────────────────────────────────────────┐
│ Preview: Transfer Settings to Aika_2_1                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Backup will be created: Aika_2_1.vtube.json.original    │
│                                                              │
│  Changes to be made:                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ + Add 2 hotkeys:                                     │   │
│  │   • Smile (Alt+Ctrl+1) - ToggleExpression           │   │
│  │   • Wink (Alt+Ctrl+2) - ToggleExpression            │   │
│  │                                                       │   │
│  │ + Copy 2 expression files:                           │   │
│  │   • Smile.exp3.json → Aika_2_1/Smile.exp3.json      │   │
│  │   • Wink.exp3.json → Aika_2_1/Wink.exp3.json        │   │
│  │                                                       │   │
│  │ ⚠ Warnings:                                          │   │
│  │   • 2 new hotkey IDs will be generated              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ⓘ You can restore the original by clicking "Undo" after   │
│    the transfer, or manually from the .original file.       │
│                                                              │
│  [Cancel]  [Apply Transfer]                                 │
└──────────────────────────────────────────────────────────────┘
```

**Features:**
- Clear summary of all changes
- File operations preview
- Warnings and validation results
- Explanation of safety features
- No surprises - user sees exactly what will happen

### 5.5 Profile Manager Widget

**Design:**
```
┌──────────────────────────────────────────────────────────────┐
│ VTS Settings Profiles                                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Saved Profiles:                            [New Profile ➕] │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📝 Streaming Setup                                   │   │
│  │    Created: 2026-01-15 14:30                         │   │
│  │    Type: Complete                                    │   │
│  │    VTS Version: 1.32.67                              │   │
│  │    [Load] [Compare] [Export] [Delete]                │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 📝 Recording Setup                                   │   │
│  │    Created: 2026-01-10 09:15                         │   │
│  │    Type: Tracking Only                               │   │
│  │    VTS Version: 1.32.67                              │   │
│  │    [Load] [Compare] [Export] [Delete]                │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ 📝 Test Configuration                                │   │
│  │    Created: 2026-01-08 16:45                         │   │
│  │    Type: Custom                                      │   │
│  │    VTS Version: 1.32.67                              │   │
│  │    [Load] [Compare] [Export] [Delete]                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Import Profile...]                                         │
└──────────────────────────────────────────────────────────────┘
```

### 5.6 Backup/Restore Widget

**Design:**
```
┌──────────────────────────────────────────────────────────────┐
│ Complete Configuration Backup                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Create Backup:                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Include:                                             │   │
│  │ ☑ Global settings (vts_config.json)                 │   │
│  │ ☑ All model configs (11 models)                     │   │
│  │ ☑ All item configs (25 items)                       │   │
│  │ ☑ Custom parameters                                 │   │
│  │ ☑ Calibration data                                  │   │
│  │ ☐ Plugin auth tokens (⚠ sensitive)                 │   │
│  │ ☑ Visual effects settings                           │   │
│  │                                                      │   │
│  │ Notes: [Text field for backup description]          │   │
│  │                                                      │   │
│  │ Save Location: [D:\VTS_Backups\] [Browse...]        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Create Backup ZIP]                                         │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│                                                              │
│  Restore from Backup:                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Backup File: [backup_20260115_1430.zip] [Browse...] │   │
│  │                                                      │   │
│  │ Contents:                                            │   │
│  │ ☑ vts_config.json (Created: 2026-01-15 14:30)       │   │
│  │ ☑ 11 model configs                                  │   │
│  │ ☑ 25 item configs                                   │   │
│  │ ☑ custom_parameters.json                            │   │
│  │                                                      │   │
│  │ ⚠ This will create a backup of your current config │   │
│  │   before restoring.                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Restore from ZIP]                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Data Structures

### 6.1 Model Configuration

```python
@dataclass
class ModelConfig:
    """Parsed .vtube.json configuration."""
    
    # Identity
    model_id: str
    name: str
    version: int
    
    # File references
    icon: str
    model_file: str
    idle_animation: str
    
    # Settings
    position: ModelPosition
    physics: PhysicsSettings
    general: GeneralSettings
    
    # Hotkeys and parameters
    hotkeys: List[Hotkey]
    parameter_settings: List[ParameterMapping]
    
    # Metadata
    metadata: ModelSaveMetadata
    saved_expressions: List[str]
    
    # Folder structure
    folder_info: FolderInfo
```

### 6.2 Hotkey Configuration

```python
@dataclass
class Hotkey:
    """Individual hotkey configuration."""
    
    hotkey_id: str  # UUID (32 hex chars)
    name: str
    action: HotkeyAction  # Enum: ToggleExpression, TriggerAnimation, etc.
    file: str  # Expression/animation filename
    folder: str  # UI folder grouping
    
    triggers: HotkeyTriggers
    is_global: bool
    is_active: bool
    
    # Advanced settings
    twitch_triggers: Optional[TwitchTriggers]
    hand_gesture_settings: Optional[HandGestureSettings]
    color_overlay: Optional[ColorOverlay]
    
    # Timing
    deactivate_after_seconds: bool
    deactivate_after_seconds_amount: float
    fade_seconds_amount: float
    
    # UI
    position: HotkeyPosition
    on_screen_hotkey_color: ColorRGBA
    minimized: bool
```

### 6.3 Transfer Result

```python
@dataclass
class TransferResult:
    """Result of a settings transfer operation."""
    
    success: bool
    backup_path: Optional[Path]
    
    # What was transferred
    hotkeys_added: int
    parameters_added: int
    files_copied: int
    
    # Issues
    warnings: List[str]
    errors: List[str]
    
    # Changes
    changes_summary: str
    detailed_log: List[str]
    
    # Rollback info
    can_undo: bool
    undo_backup_path: Optional[Path]
```

### 6.4 Profile Configuration

```python
@dataclass
class VTSProfile:
    """VTS global settings profile."""
    
    name: str
    created_date: datetime
    vts_version: str
    category: ProfileCategory  # Enum: Complete, Tracking, API, UI, Custom
    
    # Settings data (key-value pairs)
    string_data: List[ConfigEntry]
    int_data: List[ConfigEntry]
    float_data: List[ConfigEntry]
    bool_data: List[ConfigEntry]
    
    # Metadata
    description: str
    tags: List[str]
    user_notes: str
```

### 6.5 Backup Metadata

```python
@dataclass
class BackupMetadata:
    """Metadata for a complete configuration backup."""
    
    backup_date: datetime
    vts_version: str
    vts_install_path: str
    
    # Contents
    included_files: List[str]
    model_count: int
    item_count: int
    
    # User info
    user_notes: str
    backup_reason: str
    
    # Validation
    checksum: str
    file_hashes: Dict[str, str]
```

---

## 7. Safety & Validation

### 7.1 Automatic Backup System

**When Backups are Created:**
- Before any model config modification
- Before profile load operation
- Before restore operation
- Before bulk transfer operation

**Backup Naming:**
```
[ModelName].vtube.json.original       # First backup (manual restore)
[ModelName].vtube.json.backup_[timestamp]  # Additional timestamped backups
```

**Backup Retention:**
- Keep `.original` file indefinitely (manual cleanup only)
- Keep last 10 timestamped backups per model
- Backup folder location: `vts-control-panel/backups/`

### 7.2 Validation Checks

**Before Transfer:**
1. ✅ Source model config is valid JSON
2. ✅ Target model config is valid JSON
3. ✅ Source model exists and is readable
4. ✅ Target model exists and is writable
5. ✅ Expression files exist (if transferring)
6. ✅ Target has required parameters (if transferring params)
7. ✅ No UUID conflicts (if not generating new IDs)
8. ✅ File paths are valid

**During Transfer:**
1. ✅ Backup created successfully
2. ✅ Files copied successfully
3. ✅ JSON modifications are valid
4. ✅ All references updated correctly

**After Transfer:**
1. ✅ Output JSON is valid
2. ✅ All hotkeys have valid UUIDs
3. ✅ All file references exist
4. ✅ No missing required fields
5. ✅ Configuration can be loaded by VTS

### 7.3 Error Handling

**Strategy:**
- ✅ Validate before modification (fail fast)
- ✅ Atomic operations (all or nothing)
- ✅ Rollback on error (restore backup)
- ✅ Detailed error messages
- ✅ User notification with recovery options

**Example Error Flow:**
```python
def transfer_settings(source, target, settings):
    try:
        # Phase 1: Validate
        validation = validate_transfer(source, target, settings)
        if not validation.valid:
            show_errors(validation.errors)
            return
        
        # Phase 2: Backup
        backup_path = backup_model_config(target)
        
        # Phase 3: Transfer (atomic)
        try:
            result = perform_transfer(source, target, settings)
        except Exception as e:
            # Rollback
            restore_backup(target, backup_path)
            raise
        
        # Phase 4: Validate result
        if not validate_model_config(target):
            restore_backup(target, backup_path)
            raise ValidationError("Transfer produced invalid config")
        
        return result
        
    except Exception as e:
        show_error_dialog(f"Transfer failed: {e}\nOriginal config restored.")
        log_error(e)
```

### 7.4 Confirmation Dialogs

**When to Show:**
- Before any destructive operation
- Before loading a profile (changes current config)
- Before restoring from backup
- Before transferring settings (if no dry-run)

**Dialog Template:**
```
┌─────────────────────────────────────────────────────────┐
│ ⚠ Confirm: Load Profile "Streaming Setup"             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ This will change your current VTube Studio settings.   │
│                                                         │
│ Current settings will be backed up as:                 │
│ • vts_config.json.backup_20260115_143045              │
│                                                         │
│ Changes:                                                │
│ • API Port: 8001 → 8009                                │
│ • Tracking Quality: Level_3 → Level_5                  │
│ • FPS Limit: 60 → 120                                  │
│ • ... (17 more changes)                                │
│                                                         │
│ ☑ I understand this will modify my VTS configuration  │
│                                                         │
│ [View All Changes]  [Cancel]  [Confirm]                │
└─────────────────────────────────────────────────────────┘
```

---

## 8. File Structure

### 8.1 Project Structure After Implementation

```
vts-control-panel/
├── main.py                           (modified - add new tab)
├── config_manager.py                 (existing)
├── vts_api.py                        (existing)
├── vts_service.py                    (existing)
├── vts_params_tab.py                 (existing)
├── vts_settings_tab.py               (existing)
│
├── vts_model_manager_tab.py          ← NEW (main tab UI)
├── model_settings_manager.py         ← NEW (transfer logic)
├── vts_profile_manager.py            ← NEW (profile logic)
├── vts_backup_manager.py             ← NEW (backup logic)
├── vts_file_parser.py                ← NEW (JSON parsing)
├── vts_discovery.py                  ← NEW (VTS discovery)
│
├── ui/
│   ├── model_selector_widget.py      ← NEW
│   ├── settings_transfer_widget.py   ← NEW
│   ├── profile_manager_widget.py     ← NEW
│   └── backup_restore_widget.py      ← NEW
│
├── data/
│   ├── profiles/                     ← NEW (saved profiles)
│   │   ├── streaming_setup.json
│   │   ├── recording_setup.json
│   │   └── ...
│   ├── backups/                      ← NEW (local backups)
│   │   ├── Aika_Chibi_4.vtube.json.original
│   │   ├── Aika_Chibi_4.vtube.json.backup_20260115_143000
│   │   └── ...
│   └── temp/                         ← NEW (temp extraction)
│
├── config.ini
├── custom_params.json
├── vts_auth_token.json
└── README.md
```

### 8.2 Data File Formats

#### Profile File Format
```json
{
    "profile_version": 1,
    "name": "Streaming Setup",
    "created_date": "2026-01-15T14:30:00",
    "vts_version": "1.32.67",
    "category": "complete",
    "description": "My streaming configuration",
    "tags": ["streaming", "high-quality"],
    "user_notes": "Use this for Twitch streams",
    
    "settings": {
        "StringData": [
            {"Key": "Config_APIPort", "Value": "8009"},
            {"Key": "Config_LastMicName", "Value": "Microphone"}
        ],
        "IntData": [
            {"Key": "Config_FPSOption", "Value": 2}
        ],
        "FloatData": [],
        "BoolData": [
            {"Key": "Config_StartAPI", "Value": true}
        ]
    }
}
```

#### Backup Manifest Format
```json
{
    "backup_version": 1,
    "backup_date": "2026-01-15T14:30:00",
    "vts_version": "1.32.67",
    "vts_install_path": "C:/Program Files (x86)/Steam/steamapps/common/Vtube Studio",
    
    "user_notes": "Pre-update backup",
    "backup_reason": "manual",
    
    "contents": {
        "global_config": true,
        "custom_parameters": true,
        "calibration_files": true,
        "plugin_auth": false,
        "visual_effects": true,
        
        "models": [
            {
                "name": "Aika_Chibi_4",
                "model_id": "7f4cb247da49436986a40bb9c1855d89",
                "file_path": "Live2DModels/Chibi Aika 1.2/Aika_Chibi_4.vtube.json",
                "file_hash": "sha256:..."
            }
        ],
        
        "items": []
    },
    
    "file_list": [
        "vts_config.json",
        "custom_parameters.json",
        "Live2DModels/Chibi Aika 1.2/Aika_Chibi_4.vtube.json"
    ],
    
    "checksums": {
        "vts_config.json": "sha256:...",
        "custom_parameters.json": "sha256:..."
    }
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

**Core Functions:**
- `VTSDiscovery.find_vts_installation()`
- `VTSFileParser.parse_vtube_json()`
- `VTSFileParser.validate_vtube_json()`
- `ModelSettingsManager.transfer_hotkeys()`
- `ModelSettingsManager.transfer_parameters()`
- `VTSProfileManager.save_profile()`
- `VTSProfileManager.load_profile()`
- `VTSBackupManager.create_backup()`
- `VTSBackupManager.restore_backup()`

**Test Cases:**
```python
def test_hotkey_transfer():
    """Test hotkey transfer with UUID regeneration."""
    source = load_test_model("source.vtube.json")
    target = load_test_model("target.vtube.json")
    
    settings = TransferSettings(
        selected_hotkey_ids=["hotkey1", "hotkey2"],
        generate_new_ids=True
    )
    
    result = transfer_hotkeys(source, target, settings)
    
    assert result.success
    assert len(result.hotkeys_added) == 2
    # Verify new UUIDs were generated
    assert all(hk.hotkey_id != original_id for hk in result.hotkeys_added)
```

### 9.2 Integration Tests

**Test Scenarios:**
1. Complete model transfer (all settings)
2. Selective hotkey transfer
3. Transfer with missing expression files
4. Transfer with parameter validation errors
5. Profile save and load cycle
6. Complete backup and restore
7. Restore with missing files

### 9.3 UI Tests

**Manual Test Checklist:**
- [ ] Model discovery works for Steam install
- [ ] Model discovery works for standalone install
- [ ] Thumbnails load correctly
- [ ] Model info displays correctly
- [ ] Hotkey list populates from source model
- [ ] Parameter list populates from source model
- [ ] Validation indicators show correctly (✓, ⚠, ⚠)
- [ ] Transfer preview shows correct changes
- [ ] Backup is created before transfer
- [ ] Transfer completes successfully
- [ ] Rollback works after transfer
- [ ] Profile save creates correct file
- [ ] Profile load applies settings correctly
- [ ] Backup ZIP contains correct files
- [ ] Restore from ZIP works correctly
- [ ] Error dialogs show for invalid operations

### 9.4 Safety Tests

**Destructive Operation Tests:**
1. ✅ Backup is always created before modification
2. ✅ Original config is restored if transfer fails
3. ✅ Invalid JSON is rejected before modification
4. ✅ Missing files are detected before transfer
5. ✅ User must confirm before destructive operations
6. ✅ Rollback works in all error scenarios

**Validation Tests:**
1. ✅ Invalid UUIDs are detected
2. ✅ Missing file references are detected
3. ✅ Parameter conflicts are detected
4. ✅ JSON syntax errors are detected
5. ✅ Version incompatibilities are detected

---

## 10. Future Enhancements

### 10.1 Phase 2 Features (Post-Release)

**Advanced Transfer Options:**
- Transfer with parameter remapping (auto-map parameters)
- Batch transfer (multiple source models → one target)
- Template system (save transfer templates)
- Transfer filters (e.g., "only global hotkeys")

**Cloud Sync:**
- Upload profiles to cloud storage
- Share profiles with community
- Download curated profile library
- Automatic profile versioning

**Model Comparison:**
- Visual diff between two models
- Highlight differences in settings
- Side-by-side parameter comparison
- Hotkey conflict detection

**Scheduled Backups:**
- Auto-backup on schedule (daily, weekly)
- Retention policy (keep last N backups)
- Automatic cleanup of old backups
- Backup health monitoring

### 10.2 Advanced Features

**Expression Management:**
- Browse all expressions across all models
- Find unused expressions
- Duplicate detection
- Batch rename expressions
- Expression preview

**Hotkey Manager:**
- Global hotkey overview (all models)
- Conflict detection (duplicate keybinds)
- Hotkey remapping tool
- Quick hotkey editing

**Parameter Library:**
- Save parameter mappings as presets
- Share parameter presets
- Apply preset to any model
- Parameter mapping templates

**Migration Tools:**
- Migrate from old VTS version to new
- Update deprecated settings
- Fix common configuration issues
- Batch model updates

### 10.3 Community Features

**Profile Sharing:**
- Upload profiles to community hub
- Browse and download community profiles
- Rating and comments
- Profile categories (tracking, performance, etc.)

**Model Templates:**
- Save complete model config as template
- Apply template to new models
- Template marketplace
- Template customization wizard

**Collaboration:**
- Export model settings for team members
- Import and merge settings from multiple sources
- Change tracking and versioning
- Collaboration workspace

---

## 11. Implementation Timeline

### Estimated Timeline: 6-7 weeks

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Core Infrastructure | 1 week | VTS discovery, model listing |
| Phase 2: Model Settings Transfer | 2 weeks | Hotkey & parameter transfer |
| Phase 3: Expression & File Transfer | 1 week | Expression copying |
| Phase 4: VTS Settings Profiles | 1 week | Profile save/load system |
| Phase 5: Complete Backup & Restore | 1 week | ZIP backup/restore |
| Phase 6: Polish & Safety | 1 week | Validation, error handling, docs |

**Total:** 7 weeks to production-ready release

---

## 12. Success Metrics

### User Experience Metrics
- ✅ 100% of model transfers succeed without data loss
- ✅ Average transfer time < 5 seconds
- ✅ User can complete transfer workflow in < 2 minutes
- ✅ Zero reports of corrupted model configs
- ✅ Backup/restore workflow < 3 clicks

### Technical Metrics
- ✅ 100% of JSON validation passes
- ✅ Zero false positives in validation
- ✅ Backup creation < 1 second
- ✅ ZIP backup size < 10 MB (typical config)
- ✅ Restore from ZIP < 10 seconds

### Safety Metrics
- ✅ 100% of operations create backup first
- ✅ 100% rollback success rate
- ✅ Zero data loss incidents
- ✅ All destructive operations confirmed
- ✅ All errors provide recovery path

---

## 13. Documentation Requirements

### User Documentation
1. **Quick Start Guide**
   - Getting started with Model Manager
   - First model transfer walkthrough
   - Creating your first profile
   - Your first backup

2. **Feature Guides**
   - Model Settings Transfer guide
   - Profile Management guide
   - Backup & Restore guide
   - Safety best practices

3. **Troubleshooting**
   - Common issues and solutions
   - Error message reference
   - Recovery procedures
   - FAQ

### Developer Documentation
1. **Architecture Overview**
   - System design
   - Component interaction
   - Data flow diagrams

2. **API Reference**
   - Class documentation
   - Function signatures
   - Example usage

3. **Extending the System**
   - Adding new transfer types
   - Custom validation rules
   - Plugin system (future)

---

## 14. Risk Assessment & Mitigation

### Critical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss during transfer | Critical | Low | Automatic backups, validation, rollback |
| Corrupted JSON output | High | Low | JSON validation before save, schema validation |
| VTS installation not found | Medium | Medium | Manual path selection, multiple detection methods |
| UUID collision | Medium | Very Low | Generate new UUIDs, validate uniqueness |
| Expression files not found | Medium | Medium | Validation before transfer, optional file copying |
| VTS version incompatibility | Medium | Low | Version detection, warning dialogs |

### Mitigation Strategies

**For Data Loss:**
1. Always create backup before modification
2. Validate JSON before and after modification
3. Atomic operations (all or nothing)
4. Multiple rollback options (undo, restore from .original)
5. User confirmation for destructive operations

**For Discovery Failures:**
1. Multiple detection methods (registry, common paths)
2. Manual path selection as fallback
3. Remember last valid path
4. Validate path before operations

**For Validation Failures:**
1. Comprehensive validation before transfer
2. Clear error messages with resolution steps
3. Dry-run mode to preview issues
4. Automatic issue detection and suggestions

---

## 15. Conclusion

This comprehensive plan provides a complete roadmap for implementing a professional-grade VTS Model Settings Manager in the vts-control-panel app. The feature will:

1. **Empower Users** - Take control of their VTS configurations
2. **Ensure Safety** - Zero risk of data loss with automatic backups
3. **Save Time** - Transfer settings in seconds instead of manually recreating
4. **Enable Sharing** - Share profiles and templates with the community
5. **Provide Peace of Mind** - Complete backup and restore capabilities

The phased implementation approach ensures we build a solid foundation before adding advanced features. The comprehensive safety system ensures users can experiment confidently, knowing their original configurations are always protected.

---

**Next Steps:**
1. Review and approve this plan
2. Set up development environment
3. Begin Phase 1: Core Infrastructure
4. Iterate based on user feedback

**Questions? Concerns?**
Please review this plan and provide feedback before implementation begins.

---

*Document Version: 1.0*  
*Last Updated: 2026-01-15*  
*Author: AI Assistant*  
*Project: vts-control-panel Model Settings Manager*
