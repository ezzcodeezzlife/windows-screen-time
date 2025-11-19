"""
Build script for creating standalone executable using PyInstaller
"""
import PyInstaller.__main__
import os
import sys


def build():
    """Build the executable"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # PyInstaller arguments
    args = [
        'main.py',
        '--name=ScreenTimeTracker',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--icon=NONE',  # Can add icon file later if needed
        '--hidden-import=win32timezone',
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32gui',
        '--hidden-import=win32process',
        '--hidden-import=win32security',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=customtkinter',
        '--hidden-import=matplotlib',
        '--hidden-import=psutil',
        '--collect-all=customtkinter',
        '--collect-all=matplotlib',
        '--collect-all=pystray',
        '--noconfirm',  # Overwrite output without asking
    ]
    
    print("Building executable with PyInstaller...")
    print("This may take a few minutes...")
    
    try:
        PyInstaller.__main__.run(args)
        print("\nBuild complete!")
        print(f"Executable location: {os.path.join(script_dir, 'dist', 'ScreenTimeTracker.exe')}")
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()

