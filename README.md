# PC Assistant

<p align="center">
  <img src="assets/logo.png" alt="PC Assistant Logo" width="200"/>
</p>

[![CI](https://github.com/luigiellebalotta/PCAssistant/actions/workflows/ci.yml/badge.svg)](https://github.com/luigiellebalotta/PCAssistant/actions/workflows/ci.yml)
[![Release](https://github.com/luigiellebalotta/PCAssistant/actions/workflows/release.yml/badge.svg)](https://github.com/luigiellebalotta/PCAssistant/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Advanced system cleaning and optimization tool with CCleaner PRO-like features, built in Python with a modern PyQt5 interface.

## 🚀 Download

**[Download Latest Release](https://github.com/luigiellebalotta/PCAssistant/releases/latest)**

No Python installation required - just download, extract, and run!

## Features

### 🧹 System Cleaning
- Temporary files cleanup (Windows Temp, User Temp, Prefetch)
- Browser data cleaning (Chrome, Firefox, Edge)
- Recycle Bin management
- Recent files and MRU lists
- Windows log files

### 📁 Duplicate File Detection
- Hash-based content comparison (SHA256)
- Intelligent grouping of duplicates
- Preview and selective deletion
- Space savings calculation

### 🗑️ Software Management
- List all installed programs
- Track last usage date
- Identify unused software
- One-click uninstallation
- Disk space analysis per program

### 🔧 System Optimization
- Startup programs manager
- Real-time resource monitoring (CPU, RAM, Disk)
- Disk defragmentation analysis

### 🔒 Privacy & Security
- Secure file deletion (multi-pass overwrite)
- Privacy traces removal
- Registry backup before modifications

### 📊 Registry Cleaning
- Scan for obsolete entries
- Remove invalid file references
- Automatic backup and restore

## Installation

### Option 1: Download Pre-built Executable (Recommended)

1. Go to [Releases](https://github.com/luigiellebalotta/PCAssistant/releases/latest)
2. Download `PCAssistant-vX.X.X-Windows-x64.zip`
3. Extract the ZIP file
4. Run `PCAssistant.exe`
5. (Optional) Run as Administrator for full functionality

### Option 2: Run from Source

1. **Clone the repository:**
```bash
git clone https://github.com/luigiellebalotta/PCAssistant.git
cd pc_assistant
```

2. **Create virtual environment:**
```powershell
python -m venv venv
```

3. **Activate virtual environment:**
```powershell
.\venv\Scripts\Activate.ps1
```

4. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

## Usage

### Quick Launch (Recommended)

**Windows Batch:**
```cmd
run.bat
```

**PowerShell:**
```powershell
.\run.ps1
```

The launcher scripts will automatically:
- Activate the virtual environment
- Check and install dependencies if needed
- Start the application

### Manual Launch

**Run the application:**
```powershell
.\venv\Scripts\Activate.ps1
python src/main.py
```

**Note:** Some features require administrator privileges. Run as administrator for full functionality.

## Building Standalone Executable

To create a standalone .exe file that doesn't require Python installation:

### Quick Build

**Windows Batch:**
```cmd
build.bat
```

**PowerShell:**
```powershell
.\build.ps1
```

### Manual Build

```powershell
.\venv\Scripts\Activate.ps1
python build.py
```

### Build Output

Each build creates a timestamped folder in `builds/`:
```
builds/
└── build_20251204_105900/
    ├── dist/
    │   └── PCAssistant/
    │       ├── PCAssistant.exe  ← Main executable
    │       ├── config.json
    │       ├── README.md
    │       └── [dependencies]
    ├── build/                   ← Temporary build files
    ├── PCAssistant.spec        ← PyInstaller spec file
    └── BUILD_INFO.txt          ← Build information
```

**To distribute:** Zip the entire `dist/PCAssistant` folder and share it. Users can run `PCAssistant.exe` directly without installing Python.


## Project Structure

```
pc_assistant/
├── venv/                      # Virtual environment
├── src/
│   ├── core/                  # Core functionality modules
│   ├── gui/                   # PyQt5 user interface
│   ├── utils/                 # Utility functions
│   └── resources/             # Styles and icons
├── requirements.txt
└── README.md
```

## Safety Features

- ✅ Confirmation dialogs for destructive operations
- ✅ Registry backup before modifications
- ✅ Detailed operation logging
- ✅ Dry-run mode for testing
- ✅ Exclusion patterns for protected files

## Requirements

- Windows 10/11
- Python 3.8+ (for running from source)
- Administrator privileges (for some features)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- **CI**: Runs tests on every push and pull request
- **Release**: Automatically builds and publishes releases when a version tag is pushed
- **Weekly Build**: Creates development builds every Monday

### Creating a Release

To create a new release:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This will trigger the release workflow which will:
1. Build the Windows executable
2. Create a ZIP archive
3. Generate checksums
4. Create a GitHub release with downloadable assets

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- System monitoring with [psutil](https://github.com/giampaolo/psutil)
- Windows integration with [pywin32](https://github.com/mhammond/pywin32)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/luigiellebalotta/PCAssistant/issues).

---

**Note:** Replace `USERNAME` with your actual GitHub username throughout this README.
