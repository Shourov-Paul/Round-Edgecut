# KiCad Rounded Rectangle Board Outline Plugin

A professional Python-based Action Plugin for KiCad 7.0 and 8.0 that automatically generates a precisely centered, rounded rectangle board outline directly on the `Edge.Cuts` layer.

## Features
- **Specify dimensions:** Easily input Width, Height, and Corner Radius in millimeters.
- **Smart clamping:** Automatically prevents the radius from exceeding physical limits (half the shortest side).
- **Zero radius:** Generates a perfect sharp rectangle if the radius is set to 0.
- **Live Preview:** Built-in wxPython preview panel updates in real-time as you type.
- **Clean existing geometry:** Optional checkbox to automatically clear any existing `Edge.Cuts` drawings.
- **Center control:** Checkbox to draw centered at origin `(0,0)`, or default to centering in the page layout.
- **Remember settings:** Automatically saves your last used inputs for the next time you use it.

## Installation

### 1. Locate your KiCad plugin directory
- **Windows (KiCad 8.0):** `%USERPROFILE%\Documents\KiCad\8.0\scripting\plugins`
- **Windows (KiCad 7.0):** `%USERPROFILE%\Documents\KiCad\7.0\scripting\plugins`
- **Linux:** `~/.local/share/kicad/8.0/scripting/plugins`
- **macOS:** `~/Documents/KiCad/8.0/scripting/plugins`

### 2. Copy the plugin
Copy or symlink this entire `rounded_rect_plugin` folder into that plugin directory.

Ensure the structure looks like this:
```
plugins/
  └─ rounded_rect_plugin/
       ├─ __init__.py
       ├─ plugin_action.py
       ├─ dialog.py
       └─ README.md
```

### 3. Reload Plugins
Open the KiCad PCB Editor (`pcbnew`) and click **Tools -> External Plugins -> Refresh Plugins**.

## Usage
1. Open your PCB in KiCad.
2. Click the **Rounded Rectangle Outline** button in the top toolbar (or via `Tools -> External Plugins`).
3. Enter your desired Width, Height, and Radius.
4. Check the preview.
5. Hit **OK** to generate the perfect outline!
