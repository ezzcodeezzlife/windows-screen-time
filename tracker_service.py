"""
Background service for tracking active window/applications
Monitors screen time per application
"""
import time
import threading
import win32gui
import win32process
import psutil
from datetime import datetime


class TrackerService:
    """Service that tracks active window usage"""
    
    def __init__(self, database, poll_interval=2):
        """
        Initialize tracker service
        
        Args:
            database: Database instance for storing data
            poll_interval: Seconds between polls (default: 2)
        """
        self.database = database
        self.poll_interval = poll_interval
        self.running = False
        self.current_app = None
        self.app_start_time = None
        self.tracking_paused = False
        self.lock = threading.Lock()
    
    def get_active_window_info(self):
        """Get information about the currently active window"""
        try:
            # Get foreground window handle
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                # Remove .exe extension if present
                if process_name.endswith('.exe'):
                    process_name = process_name[:-4]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            # Use process name as app identifier, fallback to window title
            app_name = process_name if process_name != "Unknown" else window_title
            
            # Filter out system processes and desktop
            if app_name.lower() in ['dwm', 'explorer', 'winlogon', 'csrss', 'lsass']:
                return None
            
            return {
                'app_name': app_name,
                'window_title': window_title,
                'pid': pid
            }
        except Exception as e:
            print(f"Error getting active window: {e}")
            return None
    
    def normalize_app_name(self, app_name):
        """Normalize app name for consistent tracking"""
        # Remove common suffixes
        app_name = app_name.replace('.exe', '')
        app_name = app_name.replace('.EXE', '')
        
        # Common app name mappings
        mappings = {
            'chrome': 'Google Chrome',
            'msedge': 'Microsoft Edge',
            'firefox': 'Mozilla Firefox',
            'code': 'Visual Studio Code',
            'notepad++': 'Notepad++',
            'devenv': 'Visual Studio',
            'winword': 'Microsoft Word',
            'excel': 'Microsoft Excel',
            'powerpnt': 'Microsoft PowerPoint',
            'outlook': 'Microsoft Outlook',
            'discord': 'Discord',
            'spotify': 'Spotify',
            'steam': 'Steam',
            'vlc': 'VLC Media Player',
        }
        
        app_lower = app_name.lower()
        for key, value in mappings.items():
            if key in app_lower:
                return value
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in app_name.split())
    
    def record_app_time(self, app_name, duration_seconds):
        """Record app usage time to database"""
        if duration_seconds > 0 and app_name:
            normalized_name = self.normalize_app_name(app_name)
            self.database.record_app_usage(normalized_name, duration_seconds)
    
    def start(self):
        """Start the tracking service"""
        self.running = True
        print("Screen Time Tracker started")
        
        while self.running:
            try:
                if not self.tracking_paused:
                    window_info = self.get_active_window_info()
                    
                    if window_info:
                        current_app = window_info['app_name']
                        
                        with self.lock:
                            # If app changed, record previous app time
                            if self.current_app and self.current_app != current_app:
                                if self.app_start_time:
                                    duration = time.time() - self.app_start_time
                                    self.record_app_time(self.current_app, int(duration))
                            
                            # Update current app
                            if self.current_app != current_app:
                                self.current_app = current_app
                                self.app_start_time = time.time()
                            elif self.app_start_time is None:
                                self.app_start_time = time.time()
                    else:
                        # No active window or system process
                        with self.lock:
                            if self.current_app and self.app_start_time:
                                duration = time.time() - self.app_start_time
                                self.record_app_time(self.current_app, int(duration))
                                self.current_app = None
                                self.app_start_time = None
                
                # Sleep for poll interval
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error in tracking loop: {e}")
                time.sleep(self.poll_interval)
        
        # Record final app time when stopping
        with self.lock:
            if self.current_app and self.app_start_time:
                duration = time.time() - self.app_start_time
                self.record_app_time(self.current_app, int(duration))
    
    def stop(self):
        """Stop the tracking service"""
        self.running = False
        print("Screen Time Tracker stopped")
    
    def pause(self):
        """Pause tracking"""
        with self.lock:
            # Record current app time before pausing
            if self.current_app and self.app_start_time:
                duration = time.time() - self.app_start_time
                self.record_app_time(self.current_app, int(duration))
                self.current_app = None
                self.app_start_time = None
            self.tracking_paused = True
    
    def resume(self):
        """Resume tracking"""
        with self.lock:
            self.tracking_paused = False
    
    def is_paused(self):
        """Check if tracking is paused"""
        return self.tracking_paused

