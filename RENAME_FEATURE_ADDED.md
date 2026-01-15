# 🎯 Model Rename Feature Added!

**Date:** 2026-01-15  
**Feature:** Rename/Duplicate Models Properly

---

## ✅ What's New

### Model Rename Feature

You can now properly rename models directly from the UI! This fixes the issue where copying and renaming a model folder doesn't show up correctly in VTS.

**What it does:**
1. Renames the model folder
2. Renames the `.vtube.json` file inside
3. Updates the `Name` field in the JSON
4. Optionally generates a new `ModelID` (for duplicates)
5. Creates automatic backup before changes

---

## 🎮 How to Use

### Rename a Model

1. **Go to Model Manager tab**
2. **Select a model** from either dropdown (Source or Target)
3. **Click the "✏ Rename" button** next to the dropdown
4. **Make sure VTube Studio is closed** (confirm the warning)
5. **Enter new model name**
6. **Choose options:**
   - ✅ **"Create new Model ID"** (recommended for duplicates)
     - VTS treats it as a completely new model
     - Independent settings and hotkeys
   - ❌ Uncheck if you just want to rename (not recommended if original exists)
7. **Click "Rename Model"**
8. **Check the result** - shows all changes made
9. **Model list refreshes** automatically

---

## 📋 What Gets Changed

When you rename a model, the system:

1. **Creates backup**: `[ModelName].backup_[timestamp].json`
2. **Updates JSON content**: Changes the `Name` field
3. **Generates new ID** (if selected): Creates unique `ModelID`
4. **Renames .vtube.json**: `OldName.vtube.json` → `NewName.vtube.json`
5. **Renames folder**: `OldFolder/` → `NewFolder/`
6. **Deletes old file**: Removes the old `.vtube.json` (backup exists)

---

## 🎯 Use Cases

### Duplicate a Model
1. Close VTube Studio
2. Copy model folder in Windows Explorer
3. Rename the copied folder (e.g., "Aika" → "Aika Test")
4. Open vts-control-panel
5. Select the copied model
6. Click "Rename"
7. Keep "Create new Model ID" checked ✅
8. Enter proper name
9. Done! Model now shows correctly

### Just Rename a Model
1. Close VTube Studio
2. Select model in vts-control-panel
3. Click "Rename"
4. Uncheck "Create new Model ID" (use with caution!)
5. Enter new name
6. Done!

---

## ⚠️ Important Notes

### Before Renaming

- **Close VTube Studio** before renaming
- The system creates automatic backups
- Invalid characters are rejected (`< > : " / \ | ? *`)

### About Model ID

**When to generate new ID (recommended):**
- You duplicated a model
- You want VTS to treat it as separate
- You want independent settings

**When to keep same ID:**
- You're just fixing a typo in the name
- The original model no longer exists
- You know what you're doing

**Why it matters:**
- VTS uses `ModelID` to identify models
- Same ID = VTS thinks it's the same model
- Different ID = VTS thinks it's a new model

---

## 🔧 Technical Details

### Files Modified/Created

**New Files:**
- `model_rename_dialog.py` - UI dialog for rename
- `model_renamer.py` - Rename logic
- `RENAME_FEATURE_ADDED.md` - This document

**Modified Files:**
- `vts_model_manager_tab.py` - Added rename button and logic

### Safety Features

1. **Validation before rename**
   - Checks model folder exists
   - Verifies .vtube.json file exists
   - Checks for invalid characters
   - Prevents duplicate names

2. **Automatic backup**
   - Timestamped backup of original .vtube.json
   - Stays in the model folder

3. **Atomic operations**
   - All changes succeed or all fail
   - Rollback on error (where possible)

4. **Detailed logging**
   - Every step logged
   - Check `vts_control_panel.log` for details

---

## 🐛 Troubleshooting

### "Rename Failed" Error

**Check:**
- VTube Studio is closed
- You have write permissions
- Model folder exists
- No invalid characters in name
- Name doesn't already exist

**Solutions:**
- Close VTube Studio
- Run as administrator if needed
- Check logs: `vts_control_panel.log`
- Try a different name

### Model Not Showing After Rename

**Check:**
- Refresh the model list (re-open tab)
- Check VTS is discovering the new folder
- Verify .vtube.json has correct Name field

**Solutions:**
- Click "Discover VTS" button
- Restart vts-control-panel
- Check the renamed folder manually

### Backup File Shows in Model List

**This is normal:**
- Backup files are intentionally ignored
- If one shows up, it's not a proper backup name
- Backups should be: `[name].backup_[timestamp].json`

---

## 📝 Example Scenario

### Problem: Copied model not showing correctly

**Original situation:**
```
Live2DModels/
  Aika/
    Aika.vtube.json (Name: "Aika", ID: abc123...)
```

**You copy the folder:**
```
Live2DModels/
  Aika/
    Aika.vtube.json (Name: "Aika", ID: abc123...)
  Aika Copy/
    Aika.vtube.json (Name: "Aika", ID: abc123...)  ← PROBLEM!
```

**VTS sees:**
- One model named "Aika" (conflicting IDs)
- Doesn't show "Aika Copy" because .vtube.json still says "Aika"

**Solution using Rename feature:**

1. Select "Aika Copy" folder
2. Click "Rename"
3. Enter "Aika Test"
4. Keep "Create new Model ID" checked
5. Click "Rename Model"

**Result:**
```
Live2DModels/
  Aika/
    Aika.vtube.json (Name: "Aika", ID: abc123...)
  Aika Test/
    Aika Test.vtube.json (Name: "Aika Test", ID: xyz789...)  ← FIXED!
    Aika.backup_20260115_120000.json (backup)
```

**VTS now sees:**
- Model "Aika" (ID: abc123)
- Model "Aika Test" (ID: xyz789) ✅

---

## 🎉 Summary

The rename feature solves the common problem of copied models not showing up correctly. It handles all the necessary file operations automatically and safely.

**Key benefits:**
- ✅ No manual JSON editing needed
- ✅ Automatic backups
- ✅ Validation and error checking
- ✅ Proper ModelID handling
- ✅ Easy to use UI

**Just select, click, rename, done!** 🚀

---

## 🔜 Future Enhancements (If Needed)

- Batch rename multiple models
- Duplicate model in one step (copy + rename)
- Rename undo/redo
- Model template system
- Bulk ModelID regeneration

For now, the feature is complete and ready to use!
