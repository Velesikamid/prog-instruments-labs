"""
Модуль для управления настройками с поддержкой конфигурации.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from config_manager import get_config_value
from my_json import read_json

logger = logging.getLogger(__name__)


class SettingsManager:
    """
    Менеджер настроек приложения.
    """
    
    def __init__(self):
        self.settings: Optional[Dict[str, Any]] = None
        self.config_settings_path = get_config_value("paths.settings", "settings.json")
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Загружает настройки, объединяя из разных источников.
        
        Returns:
            Словарь с настройками
        """
        settings = {}
        
        try:
            base_settings = read_json(str(self.config_settings_path))
            settings.update(base_settings)
            logger.debug(f"Базовые настройки загружены из {self.config_settings_path}")
        except FileNotFoundError:
            logger.warning(f"Базовый файл настроек не найден: {self.config_settings_path}")
            settings = self._create_default_settings()
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            settings = self._create_default_settings()
        
        try:
            config_vk = get_config_value("vk", {})
            if config_vk:
                if "vk" not in settings:
                    settings["vk"] = {}
                settings["vk"].update(config_vk)
            
            api_version = get_config_value("parser.api_version")
            if api_version:
                settings["v"] = api_version
        except Exception as e:
            logger.warning(f"Не удалось загрузить настройки из конфигурации: {e}")
        
        self.settings = settings
        return settings
    
    def _create_default_settings(self) -> Dict[str, Any]:
        """
        Создаёт настройки по умолчанию.
        
        Returns:
            Словарь с настройками по умолчанию
        """
        return {
            "access_token": "",
            "v": "5.199",
            "offset": 0,
            "blacklist": [
                "самарский университет",
                "сгспу",
                "сниу",
                "группа",
                "им. королёва",
                "самарский государственный университет",
                "\n"
            ]
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение настройки.
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки
        """
        if self.settings is None:
            self.load_settings()
        
        return self.settings.get(key, default)
    
    def update(self, key: str, value: Any, save: bool = False) -> None:
        """
        Обновляет значение настройки.
        
        Args:
            key: Ключ настройки
            value: Новое значение
            save: Сохранять ли в файл
        """
        if self.settings is None:
            self.load_settings()
        
        self.settings[key] = value
        
        if save:
            self.save()
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Сохраняет настройки в файл.
        
        Args:
            path: Путь для сохранения (None для сохранения в текущий файл)
        """
        if self.settings is None:
            logger.warning("Нет настроек для сохранения")
            return
        
        save_path = path or self.config_settings_path
        
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info(f"Настройки сохранены в {save_path}")
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            raise


_settings_manager: Optional[SettingsManager] = None


def get_settings() -> Dict[str, Any]:
    """
    Получает глобальные настройки.
    
    Returns:
        Словарь с настройками
    """
    global _settings_manager
    
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    
    return _settings_manager.load_settings()


def get_setting(key: str, default: Any = None) -> Any:
    """
    Получает значение настройки.
    
    Args:
        key: Ключ настройки
        default: Значение по умолчанию
        
    Returns:
        Значение настройки
    """
    settings = get_settings()
    return settings.get(key, default)