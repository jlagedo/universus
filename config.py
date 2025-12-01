"""
Configuration management for Universus.
Loads settings from config.toml file.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Try to import tomllib (Python 3.11+) or fall back to tomli
try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        raise ImportError(
            "No TOML library found. Please install tomli: pip install tomli"
        )


class Config:
    """Configuration manager for Universus."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration from TOML file.
        
        Args:
            config_path: Path to config.toml file. If None, searches in:
                         1. Current directory
                         2. Script directory
                         3. User config directory
        """
        self._config: Dict[str, Any] = {}
        self._load_config(config_path)
    
    def _find_config_file(self, config_path: str = None) -> Path:
        """Find config.toml file in various locations."""
        if config_path:
            path = Path(config_path)
            if path.exists():
                return path
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Search locations
        search_paths = [
            Path.cwd() / "config.toml",
            Path(__file__).parent / "config.toml",
            Path.home() / ".config" / "universus" / "config.toml",
        ]
        
        for path in search_paths:
            if path.exists():
                logger.debug(f"Found config file: {path}")
                return path
        
        raise FileNotFoundError(
            f"config.toml not found in any of: {[str(p) for p in search_paths]}"
        )
    
    def _load_config(self, config_path: str = None):
        """Load configuration from TOML file."""
        path = self._find_config_file(config_path)
        logger.info(f"Loading configuration from {path}")
        
        with open(path, "rb") as f:
            self._config = tomllib.load(f)
        
        logger.debug(f"Configuration loaded: {list(self._config.keys())}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            section: Configuration section (e.g., 'api', 'database')
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        try:
            return self._config[section][key]
        except KeyError:
            logger.warning(f"Config key not found: [{section}].{key}, using default: {default}")
            return default
    
    @property
    def database(self) -> Dict[str, Any]:
        """Get database configuration section."""
        return self._config.get("database", {})
    
    @property
    def api(self) -> Dict[str, Any]:
        """Get API configuration section."""
        return self._config.get("api", {})
    
    @property
    def teamcraft(self) -> Dict[str, Any]:
        """Get Teamcraft configuration section."""
        return self._config.get("teamcraft", {})
    
    @property
    def cli(self) -> Dict[str, Any]:
        """Get CLI configuration section."""
        return self._config.get("cli", {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration section."""
        return self._config.get("logging", {})


# Global config instance
_config_instance = None


def get_config(config_path: str = None) -> Config:
    """Get or create global config instance.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def reload_config(config_path: str = None):
    """Reload configuration from file.
    
    Args:
        config_path: Optional path to config file
    """
    global _config_instance
    _config_instance = Config(config_path)
