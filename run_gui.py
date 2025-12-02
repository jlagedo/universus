#!/usr/bin/env python3
"""
Launcher script for Universus GUI.

Usage:
    python run_gui.py
    
Opens a web browser at http://localhost:8080 with the market tracker interface.
"""

import sys
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import nicegui
        return True
    except ImportError:
        return False


def init_services():
    """Initialize database, API, and service instances."""
    from config import get_config
    from database import MarketDatabase
    from api_client import UniversalisAPI
    from service import MarketService
    
    config = get_config()
    db_path = config.get('database', 'default_path', 'market_data.db')
    db = MarketDatabase(db_path)
    api = UniversalisAPI()
    service = MarketService(db, api)
    
    logger.info(f"Services initialized with database: {db_path}")
    
    return db, api, service, config


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
    
    # Import NiceGUI after dependency check
    from nicegui import ui
    from gui import UniversusGUI
    
    # Initialize services
    db, api, service, config = init_services()
    
    try:
        # Create GUI instance
        gui_app = UniversusGUI(db, api, service, config)
        
        @ui.page('/')
        async def main_page():
            """Main page entry point."""
            gui_app.build()
            await gui_app.initialize()
        
        # Run the application
        ui.run(
            title='Universus - FFXIV Market Tracker',
            port=8080,
            reload=False,
            show=True,
            favicon='🌍'
        )
    finally:
        # Ensure resources are cleaned up
        try:
            if db:
                db.close()
                logger.info("Database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
        finally:
            try:
                if api:
                    api.close()
                    logger.info("API client closed")
            except Exception as e:
                logger.error(f"Error closing API client: {e}")


if __name__ == "__main__":
    main()
