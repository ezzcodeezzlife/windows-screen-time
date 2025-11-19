"""
Auto-start manager for Windows
Registers application to start on Windows boot
"""
import win32api
import win32con
import win32security
import sys
import os


class AutoStartManager:
    """Manages Windows auto-start registration"""
    
    def __init__(self, app_name="ScreenTimeTracker"):
        """
        Initialize auto-start manager
        
        Args:
            app_name: Name of the application in registry
        """
        self.app_name = app_name
        self.registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def get_exe_path(self):
        """Get the path to the current executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script
            # Return path to main.py (will be replaced with .exe path after build)
            script_path = os.path.abspath(sys.argv[0])
            return script_path
    
    def is_enabled(self):
        """Check if auto-start is enabled"""
        try:
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                win32con.KEY_READ
            )
            
            try:
                value, _ = win32api.RegQueryValueEx(key, self.app_name)
                win32api.RegCloseKey(key)
                return True
            except Exception:
                win32api.RegCloseKey(key)
                return False
        except Exception as e:
            print(f"Error checking auto-start: {e}")
            return False
    
    def enable(self):
        """Enable auto-start"""
        try:
            exe_path = self.get_exe_path()
            
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                win32con.KEY_WRITE
            )
            
            win32api.RegSetValueEx(
                key,
                self.app_name,
                0,
                win32con.REG_SZ,
                exe_path
            )
            
            win32api.RegCloseKey(key)
            return True
        except Exception as e:
            print(f"Error enabling auto-start: {e}")
            return False
    
    def disable(self):
        """Disable auto-start"""
        try:
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                win32con.KEY_WRITE
            )
            
            try:
                win32api.RegDeleteValue(key, self.app_name)
                win32api.RegCloseKey(key)
                return True
            except Exception:
                win32api.RegCloseKey(key)
                return False
        except Exception as e:
            print(f"Error disabling auto-start: {e}")
            return False

