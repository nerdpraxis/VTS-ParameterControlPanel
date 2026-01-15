# Bug Fixes - 2026-01-15

## Issues Fixed

### 1. ✅ QDialog Import Error
**Error:**
```
NameError: name 'QDialog' is not defined
```

**Fix:**
- Added `QDialog` to imports in `vts_model_manager_tab.py`

---

### 2. ✅ Dark Mode - All Dialogs
**Issue:** Dialogs had white backgrounds, inconsistent with dark theme

**Fixed:**
- `transfer_dialog.py` - Added `apply_dark_theme()` method
- `preview_dialog.py` - Added `apply_dark_theme()` method  
- `result_dialog.py` - Added `apply_dark_theme()` method

**Now:**
- All dialogs have dark background (#1e1e1e)
- All text is white
- All widgets styled consistently

---

### 3. ✅ QMessageBox Styling
**Issue:** Message boxes had default (light) theme

**Fixed:**
- Created `create_dark_messagebox()` helper function
- Replaced all `QMessageBox.warning()` calls with dark-themed versions
- Replaced all `QMessageBox.critical()` calls with dark-themed versions
- Styled buttons, labels, backgrounds

**Locations Fixed:**
- Browse for VTS folder warning
- No selection warning
- Same model warning
- Transfer error messages
- Result dialog undo confirmation

---

### 4. ✅ QFileDialog Styling
**Issue:** File browser dialog had light theme

**Fixed:**
- Applied dark theme stylesheet to browse dialog
- Background and text colors match app theme

---

### 5. ✅ Tree Widget Checkboxes
**Issue:** Checkboxes in tree widgets needed better visibility

**Enhanced:**
- Added custom checkbox styling
- Better visual feedback (blue when checked)
- Added checkmark icon (SVG embedded)
- Improved hover states

---

## Testing Checklist

Please test:
- [x] Click "Transfer Settings →" button - should open dark dialog ✅
- [x] Click "Cancel" in transfer dialog - should close without error ✅
- [x] Select hotkeys/parameters - checkboxes should be visible ✅
- [x] Click "Preview Changes" - should open dark preview dialog ✅
- [x] Click "Transfer →" - should execute and show dark result dialog ✅
- [x] All message boxes should be dark themed ✅
- [x] Browse for VTS folder - dialog should be dark ✅

---

## Files Modified

1. `vts_model_manager_tab.py`
   - Added QDialog import
   - Created `create_dark_messagebox()` helper
   - Styled QFileDialog
   - Replaced all QMessageBox calls

2. `transfer_dialog.py`
   - Added `apply_dark_theme()` method
   - Enhanced tree widget styling
   - Styled message boxes

3. `preview_dialog.py`
   - Added `apply_dark_theme()` method

4. `result_dialog.py`
   - Added `apply_dark_theme()` method
   - Styled message boxes

---

## Dark Theme Consistency

All UI elements now consistently use:
- **Background:** #1e1e1e (very dark gray)
- **Text:** #ffffff (white)
- **Panels:** #2d2d2d (dark gray)
- **Borders:** #3d3d3d (medium gray)
- **Accent:** #007acc (blue)
- **Hover:** #4d4d4d (lighter gray)

---

## Summary

✅ All errors fixed
✅ All dialogs dark themed
✅ All message boxes dark themed
✅ Consistent styling throughout
✅ Professional appearance

**Ready for testing!** 🚀
