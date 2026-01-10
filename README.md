# VTS Control Panel

A standalone VTube Studio parameter controller that allows you to create, manage, and animate custom parameters for your VTube Studio model.

![VTS Control Panel](https://img.shields.io/badge/VTube%20Studio-Plugin-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-orange)

## Features

- ✨ **Real-time Parameter Control** - Create and manage custom VTube Studio parameters
- 🎭 **Live Animation** - Animate your model with mathematical functions (sine, cosine, random waves, etc.)
- 📊 **Multiple Animation Types** - Choose from various mathematical functions for natural movement
- ⚡ **Heartbeat System** - Real-time parameter value generation and sending
- 🎮 **Easy Connection** - Simple WebSocket connection to VTube Studio
- 💾 **Parameter Persistence** - Save and load parameter configurations
- 🔍 **Filter & Search** - Quickly find parameters in large setups
- 🎨 **Dark Theme UI** - Modern, easy-on-the-eyes interface

## Requirements

- **Windows 10/11**
- **Python 3.11** (included in venv)
- **VTube Studio** (running and API enabled)
- **PyQt6** (installed in venv)
- **websockets** library (installed in venv)

## Setup Guide

### 1. Prerequisites

1. **Install VTube Studio**
   - Download from [Steam](https://store.steampowered.com/app/1325860/VTube_Studio/) or [Official Website](https://denchisoft.com/)
   - Launch VTube Studio and load a model

2. **Enable VTube Studio API**
   - In VTube Studio, go to Settings
   - Enable "API" in the settings
   - Note the port number (default: 8001)

### 2. Installation

#### Option A: Run from Source (Recommended for Development)

```bash
# Navigate to the vts-control-panel folder
cd vts-control-panel

# Run using the batch script
run.bat

# OR run directly with Python
..\venv_py311\Scripts\python.exe main.py
```

#### Option B: Build Executable (For Distribution)

```bash
# Navigate to the vts-control-panel folder
cd vts-control-panel

# Run the build script
build_exe.bat

# The executable will be in the dist folder
cd dist
VTS-Control-Panel.exe
```

### 3. First Time Setup

1. **Launch the Application**
   - Run `run.bat` or the built executable

2. **Configure Connection**
   - Go to the **Settings** tab
   - Enter the VTube Studio API URL (default: `ws://localhost:8001/`)
   - Click **Connect**
   - Approve the authentication request in VTube Studio when prompted

3. **Start Using**
   - Go to the **VTS Parameters** tab
   - Add parameters or load existing ones
   - Enable parameters and click **▶ Start Heartbeat** to animate your model

## User Interface Guide

### VTS Parameters Tab

The main tab where you create and manage parameters.

#### Top Section (Fixed)
- **Filter Bar** - Search/filter parameters by name (always visible at top)
- **Clear Button** - Clear the filter

#### Middle Section (Scrollable)
- **Parameter Cards** - Each parameter has its own card with all controls
- Scroll through your parameters while keeping filter and buttons visible

#### Bottom Section (Fixed)
- **Add Parameter** - Create a new parameter
- **Save Parameters** - Save current configuration to JSON
- **Refresh** - Reload parameters from JSON file
- **Extract from VTube** - Import parameters from currently loaded VTS model
- **Disable All** - Quickly disable all parameters at once
- **▶ Start Heartbeat** - Begin real-time parameter animation

### Parameter Controls Explained

Each parameter card contains:

#### Basic Settings

| Control | Description |
|---------|-------------|
| **Parameter Name** | Unique identifier for the parameter in VTube Studio |
| **Enabled Checkbox** | Enable/disable this parameter's animation |
| **Min/Max Values** | Range limits for the parameter (-10 to 10 for rotation, -1 to 1 for others) |
| **Default Value** | Starting value when parameter is created |

#### Animation Settings

| Control | Description |
|---------|-------------|
| **Math Function** | Choose animation type:<br>• **Sine Wave** - Smooth oscillation<br>• **Cosine Wave** - Sine wave offset by 90°<br>• **Triangle Wave** - Linear up/down movement<br>• **Square Wave** - Sharp on/off switching<br>• **Sawtooth Wave** - Ramp up then instant drop<br>• **Random Wave** - Natural random movement<br>• **Gaussian Wave** - Bell curve oscillation<br>• **Perlin Noise** - Smooth organic noise |
| **Math Frequency** | How fast the wave cycles (higher = faster oscillation) |
| **Math Amplitude** | Height of the wave (how far from center it moves) |
| **Math Offset** | Baseline shift (moves the whole wave up/down) |
| **Generation Speed** | Overall speed multiplier for value generation |
| **Values Per Second** | How many times per second to update this parameter |

#### Pause Patterns

Create breathing/idle patterns by adding pauses:

| Control | Description |
|---------|-------------|
| **Enable Pause** | Toggle pause pattern on/off |
| **Pause Duration** | How long to hold the pause value (seconds) |
| **Pause Interval** | Time between pauses (seconds) |
| **Pause Value** | What value to hold during pause |
| **Duration Random %** | Add variance to pause length |
| **Interval Random %** | Add variance to pause timing |
| **Amount Random %** | Add variance to pause value |

#### Randomization

Add natural variation to parameters:

| Control | Description |
|---------|-------------|
| **Enable Random** | Toggle randomization on/off |
| **Random Percent** | How much to vary the value (±percentage) |
| **Random Seed** | Seed for reproducible randomness |
| **Random Function** | Distribution type (Uniform/Gaussian/etc.) |

### Settings Tab

Configure your VTube Studio connection:

| Setting | Description |
|---------|-------------|
| **API URL** | WebSocket address of VTube Studio (default: `ws://localhost:8001/`) |
| **Auto-connect** | Automatically connect on startup |
| **Status** | Current connection status (Connected ✓ / Not connected) |
| **Connect Button** | Manually connect/disconnect |

## Common Use Cases

### 1. Idle Animation

Create subtle head movements when not talking:

1. Add parameter `FaceAngleX` (head tilt)
2. Set Math Function: **Random Wave**
3. Set Min: `-5`, Max: `5`
4. Set Math Frequency: `0.3` (slow)
5. Set Math Amplitude: `0.7` (subtle)
6. Enable Pause: Duration `3s`, Interval `8s`
7. Enable and start heartbeat

### 2. Breathing Effect

Add natural breathing movement:

1. Add parameter `BreathAmount`
2. Set Math Function: **Sine Wave**
3. Set Math Frequency: `0.2` (breathing rate)
4. Set Math Amplitude: `1.0`
5. Set Values Per Second: `10` (smooth)
6. Enable and start heartbeat

### 3. Random Blinking

Occasional random movements:

1. Add parameter `EyeOpenLeft`
2. Set Math Function: **Random Wave**
3. Enable Pause: Duration `0.2s`, Interval `4s`
4. Set Interval Random: `50%` (varies 2-6s)
5. Enable and start heartbeat

## Configuration Files

### config.ini

Stores application settings:
- VTS API URL and authentication token
- Window size and position
- Auto-connect preference
- Parameter JSON file path

### custom_params.json

Stores all your parameter configurations:
- Parameter names and ranges
- Math function settings
- Animation settings
- Pause patterns
- Randomization settings

**Tip:** You can share your `custom_params.json` file with other VTubers!

## Troubleshooting

### "Cannot connect to VTube Studio"

**Solutions:**
1. Ensure VTube Studio is running
2. Enable API in VTube Studio settings
3. Check the port number matches (default: 8001)
4. Check firewall isn't blocking the connection
5. Try `ws://localhost:8001/` or `ws://127.0.0.1:8001/`

### "Parameters not appearing in VTube Studio"

**Solutions:**
1. Make sure you clicked **Connect** in Settings tab
2. Wait for "Connected ✓" status
3. Enable at least one parameter
4. Click **▶ Start Heartbeat**
5. Check VTube Studio API logs for errors

### "Heartbeat running but model not moving"

**Solutions:**
1. Verify parameters are **Enabled** (checkbox checked)
2. Check parameter names match VTS parameter IDs
3. Ensure min/max ranges are appropriate
4. Try increasing **Math Amplitude** for more visible movement
5. Check VTube Studio model has the parameters mapped

### "Application won't start"

**Solutions:**
1. Make sure you're using Python 3.11
2. Run from the venv: `..\venv_py311\Scripts\python.exe main.py`
3. Check `vts_control_panel.log` for error messages
4. Ensure all dependencies are installed in the venv

## Building for Distribution

To create a standalone executable:

```bash
# 1. Navigate to vts-control-panel folder
cd vts-control-panel

# 2. Run build script (requires PyInstaller in venv)
build_exe.bat

# 3. Find executable in dist folder
cd dist
```

The built executable will include:
- All Python dependencies
- Configuration files
- README and documentation

## Development

### Project Structure

```
vts-control-panel/
├── main.py                 # Application entry point
├── config_manager.py       # Configuration management
├── vts_service.py         # VTS WebSocket communication
├── vts_api.py            # VTS API implementation
├── vts_params_tab.py     # Parameters UI tab
├── vts_settings_tab.py   # Settings UI tab
├── config.ini            # User configuration
├── custom_params.json    # Parameter definitions
├── run.bat               # Quick start script
└── build_exe.bat         # Build executable script
```

### Adding New Features

The codebase uses AIKA's VTS implementation:
- `vts_api.py` - Low-level WebSocket API
- `vts_service.py` - High-level service with persistent event loop
- `ui/components/vts_params.py` - Full parameter management UI (from AIKA)

## Credits

- Built on AIKA's VTube Studio integration
- Uses [VTube Studio API](https://github.com/DenchiSoft/VTubeStudio)
- UI framework: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)

## License

This project is part of the AIKA VTuber Control Panel suite.

## Support

For issues, questions, or feature requests, please check:
1. This README's troubleshooting section
2. VTube Studio API documentation
3. The `vts_control_panel.log` file for error details

---

**Made with ❤️ for VTubers**
