"""
Windows UAC and administrator privileges helper
"""
import ctypes
import sys
import os


def is_admin():
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin():
    """Request administrator privileges by restarting the application"""
    if not is_admin():
        # Re-run the program with admin rights
        try:
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:])
            
            # ShellExecute with 'runas' verb to request elevation
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1  # SW_SHOWNORMAL
            )
            return True
        except Exception as e:
            print(f"Failed to request admin privileges: {e}")
            return False
    return False


def check_admin_and_warn():
    """Check admin status and return warning message if not admin"""
    if not is_admin():
        return (
            "⚠️ Attenzione: L'applicazione non è in esecuzione con privilegi di amministratore.\n"
            "Alcune funzionalità potrebbero non funzionare correttamente:\n"
            "- Pulizia registro di Windows\n"
            "- Disinstallazione software\n"
            "- Accesso a file di sistema\n"
            "- Modifica programmi di avvio\n\n"
            "Si consiglia di riavviare come amministratore."
        )
    return None
