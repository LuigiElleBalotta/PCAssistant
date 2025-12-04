"""
Configuration manager for PC Assistant
Handles loading and saving user preferences
"""
import json
import os
from typing import Any, Dict


class Config:
    """Configuration manager"""
    
    DEFAULT_CONFIG = {
        "cleaning": {
            "temp_files": True,
            "browser_cache": True,
            "recycle_bin": False,
            "recent_files": True,
            "log_files": True
        },
        "browsers": {
            "chrome": True,
            "firefox": True,
            "edge": True
        },
        "security": {
            "secure_delete_passes": 3,
            "backup_registry": True
        },
        "duplicates": {
            "min_file_size": 1024,
            "excluded_extensions": [".sys", ".dll", ".exe"]
        },
        "software": {
            "unused_threshold_days": 90,
            "show_system_software": False
        },
        "excluded_paths": [
            "C:\\Windows",
            "C:\\Program Files\\WindowsApps"
        ],
        "ui": {
            "theme": "dark",
            "language": "it"
        }
    }
    
    def __init__(self, config_file="config.json"):
        """Initialize configuration manager"""
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save_config(self, config: Dict = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def save(self):
        """Save current configuration"""
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()


# Global config instance
_config_instance = None

def get_config():
    """Get global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
