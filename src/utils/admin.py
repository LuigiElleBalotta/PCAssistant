"""
Windows UAC and administrator privileges helper.
Falls back gracefully on non-Windows platforms.
"""
import ctypes
import sys
import os
import platform


IS_WINDOWS = platform.system() == "Windows"


def is_admin():
    """Check if the current process has administrator privileges"""
    if not IS_WINDOWS:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def request_admin():
    """Request administrator privileges by restarting the application"""
    if not IS_WINDOWS:
        return False
    if not is_admin():
        try:
            script = os.path.abspath(sys.argv[0])
            params = " ".join([script] + sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1,  # SW_SHOWNORMAL
            )
            return True
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            return False
    return False


def check_admin_and_warn():
    """Check admin status and return warning message if not admin"""
    if not IS_WINDOWS:
        # UAC prompt not applicable outside Windows
        return None
    if not is_admin():
        return (
            "ƒsÿ‹÷? Attenzione: L'applicazione non Çù in esecuzione con privilegi di amministratore.\n"
            "Alcune funzionalitÇÿ potrebbero non funzionare correttamente:\n"
            "- Pulizia registro di Windows\n"
            "- Disinstallazione software\n"
            "- Accesso a file di sistema\n"
            "- Modifica programmi di avvio\n\n"
            "Si consiglia di riavviare come amministratore."
        )
    return None
