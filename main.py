"""
Screen Time Tracker - Main Entry Point
Tracks application usage time similar to Apple's Screen Time
"""
import sys
import os
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tracker_service import TrackerService
from gui import ScreenTimeGUI
from database import Database
from autostart import AutoStartManager
import pystray
from PIL import Image, ImageDraw
import customtkinter as ctk


def create_tray_icon(tracker_service, gui):
    """Create system tray icon"""
    # Create a simple icon
    image = Image.new('RGB', (64, 64), color='#1a1a1a')
    draw = ImageDraw.Draw(image)
    draw.ellipse([16, 16, 48, 48], fill='#4a9eff', outline='#2a7fff', width=2)
    
    def show_gui(icon, item):
        """Show the GUI window"""
        gui.show_window()
    
    def quit_app(icon, item):
        """Quit the application"""
        tracker_service.stop()
        icon.stop()
        gui.root.quit()
        sys.exit(0)
    
    menu = pystray.Menu(
        pystray.MenuItem('Show Dashboard', show_gui),
        pystray.MenuItem('Quit', quit_app)
    )
    
    icon = pystray.Icon("ScreenTimeTracker", image, "Screen Time Tracker", menu)
    return icon


def main():
    """Main entry point"""
    # Initialize database
    db = Database()
    db.init_database()
    
    # Setup auto-start (if not already set)
    autostart = AutoStartManager()
    if not autostart.is_enabled():
        autostart.enable()
    
    # Initialize tracker service
    tracker_service = TrackerService(db)
    
    # Start tracking in background thread
    tracker_thread = threading.Thread(target=tracker_service.start, daemon=True)
    tracker_thread.start()
    
    # Create GUI (initially hidden)
    root = ctk.CTk()
    gui = ScreenTimeGUI(root, db, tracker_service)
    
    # Create system tray icon
    icon = create_tray_icon(tracker_service, gui)
    
    # Start tray icon in separate thread
    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()
    
    # Run GUI main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        tracker_service.stop()
        icon.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()

