"""
PC Assistant - Build Script
Creates standalone executable using PyInstaller with timestamped builds
"""
import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("PyInstaller installed successfully!")


def create_build_directory():
    """Create timestamped build directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_dir = Path("builds") / f"build_{timestamp}"
    build_dir.mkdir(parents=True, exist_ok=True)
    return build_dir


def build_executable(build_dir):
    """Build executable using PyInstaller"""
    print("\n" + "="*50)
    print("Building PC Assistant executable...")
    print("="*50 + "\n")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=PCAssistant",
        "--onedir",  # Create a folder with dependencies
        "--windowed",  # No console window
        "--icon=NONE",  # Add icon path if you have one
        f"--distpath={build_dir / 'dist'}",
        f"--workpath={build_dir / 'build'}",
        f"--specpath={build_dir}",
        "--paths=src",  # Add src to Python path
        "--add-data=src/resources;resources",  # Include resources
        "--add-data=config.json;.",  # Include config
        # Hidden imports for all our modules
        "--hidden-import=gui.main_window",
        "--hidden-import=gui.dashboard_tab",
        "--hidden-import=gui.cleaner_tab",
        "--hidden-import=gui.tools_tab",
        "--hidden-import=gui.disk_analyzer_tab",
        "--hidden-import=gui.optimizer_tab",
        "--hidden-import=gui.settings_tab",
        "--hidden-import=core.cleaner",
        "--hidden-import=core.duplicate_finder",
        "--hidden-import=core.software_manager",
        "--hidden-import=core.registry_manager",
        "--hidden-import=core.optimizer",
        "--hidden-import=core.secure_delete",
        "--hidden-import=core.analyzer",
        "--hidden-import=utils.logger",
        "--hidden-import=utils.config",
        "--hidden-import=utils.admin",
        "--hidden-import=utils.scanner",
        # External dependencies
        "--hidden-import=PyQt5",
        "--hidden-import=psutil",
        "--hidden-import=winshell",
        "--hidden-import=win32com",
        "--collect-all=PyQt5",
        "src/main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return False


def copy_additional_files(build_dir):
    """Copy additional files to build directory"""
    print("\nCopying additional files...")
    
    dist_dir = build_dir / "dist" / "PCAssistant"
    
    # Copy README
    if os.path.exists("README.md"):
        shutil.copy("README.md", dist_dir / "README.md")
        print("✓ Copied README.md")
    
    # Copy config
    if os.path.exists("config.json"):
        shutil.copy("config.json", dist_dir / "config.json")
        print("✓ Copied config.json")
    
    # Create logs directory
    (dist_dir / "logs").mkdir(exist_ok=True)
    print("✓ Created logs directory")
    
    # Create registry_backups directory
    (dist_dir / "registry_backups").mkdir(exist_ok=True)
    print("✓ Created registry_backups directory")


def create_build_info(build_dir):
    """Create build information file"""
    info_file = build_dir / "BUILD_INFO.txt"
    
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write("PC Assistant - Build Information\n")
        f.write("="*50 + "\n\n")
        f.write(f"Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Build Directory: {build_dir}\n")
        f.write("\nExecutable Location:\n")
        f.write(f"{build_dir / 'dist' / 'PCAssistant' / 'PCAssistant.exe'}\n")
        f.write("\nTo run the application:\n")
        f.write("1. Navigate to dist/PCAssistant/\n")
        f.write("2. Run PCAssistant.exe\n")
        f.write("3. For full functionality, run as Administrator\n")
    
    print(f"\n✓ Created build info: {info_file}")


def main():
    """Main build process"""
    print("\n" + "="*50)
    print("PC Assistant - Build System")
    print("="*50 + "\n")
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found.")
        response = input("Install PyInstaller? (y/n): ")
        if response.lower() == 'y':
            install_pyinstaller()
        else:
            print("Build cancelled.")
            return 1
    
    # Create build directory
    build_dir = create_build_directory()
    print(f"Build directory: {build_dir}\n")
    
    # Build executable
    if not build_executable(build_dir):
        print("\n❌ Build failed!")
        return 1
    
    # Copy additional files
    copy_additional_files(build_dir)
    
    # Create build info
    create_build_info(build_dir)
    
    # Success message
    print("\n" + "="*50)
    print("✅ Build completed successfully!")
    print("="*50)
    print(f"\nExecutable location:")
    print(f"{build_dir / 'dist' / 'PCAssistant' / 'PCAssistant.exe'}")
    print(f"\nBuild directory:")
    print(f"{build_dir.absolute()}")
    print("\nTo distribute:")
    print(f"Zip the entire 'dist/PCAssistant' folder")
    print("\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
