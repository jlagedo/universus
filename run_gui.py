#!/usr/bin/env python3
"""
Launcher script for Universus GUI.

Usage:
    python run_gui.py
    
Opens a web browser at http://localhost:8080 with the market tracker interface.
"""

import sys


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import nicegui
        return True
    except ImportError:
        return False


def main():
    """Main entry point."""
    if not check_dependencies():
        print("=" * 60)
        print("ERROR: NiceGUI is not installed.")
        print("=" * 60)
        print()
        print("Please install the required dependencies:")
        print()
        print("    pip install -r requirements.txt")
        print()
        print("Or install NiceGUI directly:")
        print()
        print("    pip install nicegui")
        print()
        sys.exit(1)
    
    # Import and run the GUI
    from gui import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()
