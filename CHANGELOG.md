# Changelog

All notable changes to PC Assistant will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025-12-04

### Fixed
- Fixed PyInstaller module collection issue causing "No module named 'gui'" error
- Added explicit hidden imports for all application modules (gui, core, utils)
- Added `--paths=src` to PyInstaller configuration for proper module resolution
- Fixed Unicode encoding issue in CI workflow test output

### Changed
- Updated build.py with comprehensive module imports
- Updated GitHub Actions workflows (release.yml, weekly-build.yml) with fixed PyInstaller configuration

## [1.0.0] - 2025-12-04

### Added
- System cleaning functionality
  - Temporary files cleanup
  - Browser cache cleaning (Chrome, Firefox, Edge)
  - Recycle bin management
  - Recent files cleanup
  - Windows log files cleanup
- Duplicate file detection
  - SHA256 hash-based content comparison
  - Intelligent grouping and wasted space calculation
  - Selective deletion with preview
- Software management
  - Complete list of installed programs
  - Usage tracking by file modification dates
  - One-click uninstallation
  - Disk space analysis per program
- System optimization
  - Startup programs manager
  - Real-time resource monitoring (CPU, RAM, Disk)
  - Process list with resource usage
- Security features
  - Secure file deletion (1-35 passes)
  - DOD 5220.22-M and Gutmann methods
  - Registry backup before modifications
- Registry cleaning
  - Scan for invalid paths and orphaned entries
  - Backup and restore functionality
- Modern PyQt5 GUI
  - Dark theme with teal accent
  - 5-tab interface (Dashboard, Cleaner, Tools, Optimizer, Settings)
  - Real-time status bar with system stats
  - Progress indicators and detailed logging
- Configuration system
  - JSON-based persistent settings
  - Customizable cleaning options
  - Security preferences
- Logging system
  - File rotation (10MB max, 5 backups)
  - Console and file output
  - Detailed operation tracking
- Build system
  - PyInstaller integration
  - Timestamped builds
  - Automated dependency collection
- Launcher scripts
  - Windows batch launcher (run.bat)
  - PowerShell launcher (run.ps1)
  - Automatic venv activation and dependency checking
- Documentation
  - Comprehensive README
  - Italian quick start guide (GUIDA_RAPIDA.md)
  - Complete project summary (RIEPILOGO.md)

### Security
- Administrator privilege detection and warnings
- Confirmation dialogs for destructive operations
- Automatic registry backup before modifications
- Protected system paths exclusion

[Unreleased]: https://github.com/luigiellebalotta/PCAssistant/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/luigiellebalotta/PCAssistant/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/luigiellebalotta/PCAssistant/releases/tag/v1.0.0
