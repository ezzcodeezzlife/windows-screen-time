# Screen Time Tracker

A Windows application that tracks your screen time per application, similar to Apple's Screen Time feature. Runs in the background, displays statistics in a modern GUI, and auto-starts on Windows boot.

## Features

- **Automatic Tracking**: Monitors active windows and tracks time spent in each application
- **Modern Dashboard**: Beautiful GUI with statistics, charts, and app breakdowns
- **System Tray Integration**: Runs in background with system tray icon for quick access
- **Auto-Start**: Automatically starts on Windows boot
- **Historical Data**: Stores usage data in SQLite database for historical analysis
- **Easy Distribution**: Single .exe installer for one-click installation

## Installation

### For End Users (One-Click Install)

1. Download `ScreenTimeTracker_Setup.exe`
2. Double-click to run the installer
3. Follow the installation wizard (just click "Next" through the prompts)
4. The application will automatically start and begin tracking

### For Developers

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Building the Executable

### Step 1: Build the .exe

```bash
python build.py
```

This will create `dist/ScreenTimeTracker.exe` using PyInstaller.

### Step 2: Create the Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php) (free, open-source)
2. Open `setup.iss` in Inno Setup Compiler
3. Click "Build" → "Compile" (or press F9)
4. The installer will be created in the `installer` folder as `ScreenTimeTracker_Setup.exe`

## Usage

- **View Dashboard**: Right-click the system tray icon and select "Show Dashboard"
- **Pause Tracking**: Click "Pause Tracking" in the dashboard
- **Hide to Tray**: Click "Hide to Tray" to minimize to system tray
- **Quit**: Right-click system tray icon and select "Quit"

## Data Storage

Usage data is stored in:
- Windows: `%APPDATA%\ScreenTimeTracker\screentime.db`

The database contains:
- Daily session summaries
- Per-application usage time
- Historical data for charts and statistics

## Requirements

- Windows 10 or later
- No Python installation needed (for end users using the .exe)

## Development Requirements

- Python 3.8+
- pywin32
- customtkinter
- matplotlib
- psutil
- pyinstaller
- pystray
- Pillow

## License

Free to use and distribute.

