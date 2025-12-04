"""
PC Assistant - Main Entry Point
Advanced System Cleaner and Optimizer
"""
import sys
import os

# Fix for PyQt5 slow GUI response - disable high DPI scaling
# https://stackoverflow.com/questions/61755740/pyqt5-application-slow-gui-response-for-unknown-reasons
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.logger import get_logger
from utils.config import get_config


def main():
    """Main application entry point"""
    # Initialize logger
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("PC Assistant Starting")
    logger.info("=" * 50)
    
    # Initialize config
    config = get_config()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("PC Assistant")
    app.setOrganizationName("PC Assistant")
    
    # Load stylesheet
    try:
        style_path = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
            logger.info("Stylesheet loaded successfully")
        else:
            logger.warning(f"Stylesheet not found at {style_path}")
    except Exception as e:
        logger.error(f"Error loading stylesheet: {e}")
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        logger.info("Main window displayed")
    except Exception as e:
        logger.critical(f"Failed to create main window: {e}")
        return 1
    
    # Run application
    exit_code = app.exec_()
    
    logger.info("PC Assistant Exiting")
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
