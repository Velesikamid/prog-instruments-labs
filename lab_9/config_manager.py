"""
Модуль для управления конфигурацией приложения.
Использует OmegaConf для послойной конфигурации.
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from omegaconf import OmegaConf, DictConfig


class ConfigManager:
    """
    Менеджер конфигурации с поддержкой послойных YAML-файлов.
    """
    
    def __init__(self, config_dir: str = "config", env: Optional[str] = None):
        """
        Инициализирует менеджер конфигурации.
        
        Args:
            config_dir: Директория с конфигурационными файлами
            env: Режим работы ('dev', 'prod', None для автоматического определения)
        """
        self.config_dir = Path(config_dir)
        self.env = env or self._detect_environment()
        self.config: Optional[DictConfig] = None
        
    def _detect_environment(self) -> str:
        """
        Определяет среду выполнения по переменным окружения.
        
        Returns:
            Строка с названием среды ('dev', 'prod')
        """
        env = os.getenv("APP_ENV", "").lower()
        if env in ("development", "dev", "debug"):
            return "dev"
        elif env in ("production", "prod", "release"):
            return "prod"
        
        dev_config = self.config_dir / "dev.yaml"
        prod_config = self.config_dir / "prod.yaml"
        
        if dev_config.exists():
            return "dev"
        elif prod_config.exists():
            return "prod"
        
        return "dev"
    
    def load_config(self) -> DictConfig:
        """
        Загружает конфигурацию из YAML-файлов.
        
        Returns:
            Объект конфигурации OmegaConf
        """
        base_config = self.config_dir / "base.yaml"
        if not base_config.exists():
            self._create_default_base_config()
        
        self.config = OmegaConf.load(str(base_config))
        
        env_config = self.config_dir / f"{self.env}.yaml"
        if env_config.exists():
            env_conf = OmegaConf.load(str(env_config))
            self.config = OmegaConf.merge(self.config, env_conf)
        
        local_config = self.config_dir / "local.yaml"
        if local_config.exists():
            local_conf = OmegaConf.load(str(local_config))
            self.config = OmegaConf.merge(self.config, local_conf)
        
        env_config_dict = self._load_from_env()
        if env_config_dict:
            env_conf = OmegaConf.create(env_config_dict)
            self.config = OmegaConf.merge(self.config, env_conf)
        
        OmegaConf.update(self.config, "env", self.env)
        
        self._validate_config()
        
        return self.config
    
    def _create_default_base_config(self) -> None:
        """
        Создаёт базовый конфигурационный файл по умолчанию.
        """
        base_config = self.config_dir / "base.yaml"
        self.config_dir.mkdir(exist_ok=True)
        
        default_config = {
            "app": {
                "name": "vk-parser",
                "version": "1.0.0",
                "description": "Парсер комментариев ВКонтакте"
            },
            "logging": {
                "level": "INFO",
                "to_file": True,
                "file_format": "app_%Y%m%d_%H%M%S.log",
                "dir": "logs",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "date_format": "%Y-%m-%d %H:%M:%S",
                "console": True
            },
            "filemanager": {
                "create_dirs": True,
                "overwrite": True,
                "encoding": "utf-8"
            },
            "list_of_people": {
                "pattern": r"\d{4}[-–]\d{2}.?\d{2}.?\d{2}[a-zа-я]?",
                "default_is_students": False
            },
            "parser": {
                "vk_api_url": "https://api.vk.com/method/board.getComments",
                "api_version": "5.199",
                "timeout": 30,
                "max_retries": 3,
                "batch_size": 100,
                "offset": 0
            },
            "json": {
                "encoding": "utf-8-sig"
            },
            "paths": {
                "settings": "settings.json",
                "output_dir": "results",
                "default_output": "output.txt"
            }
        }
        
        import yaml
        with open(base_config, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"Создан базовый конфигурационный файл: {base_config}")
    
    def _load_from_env(self) -> Dict[str, Any]:
        """
        Загружает конфигурацию из переменных окружения.
        
        Returns:
            Словарь с конфигурацией из переменных окружения
        """
        env_config = {}
        
        vk_token = os.getenv("VK_ACCESS_TOKEN")
        if vk_token:
            env_config["vk"] = {"access_token": vk_token}
        
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            if "logging" not in env_config:
                env_config["logging"] = {}
            env_config["logging"]["level"] = log_level
        
        output_dir = os.getenv("OUTPUT_DIR")
        if output_dir:
            if "paths" not in env_config:
                env_config["paths"] = {}
            env_config["paths"]["output_dir"] = output_dir
        
        return env_config
    
    def _validate_config(self) -> None:
        """
        Валидирует загруженную конфигурацию.
        
        Raises:
            ValueError: Если конфигурация некорректна
        """
        if not self.config:
            raise ValueError("Конфигурация не загружена")
        
        if self.env == "prod":
            vk_token = OmegaConf.select(self.config, "vk.access_token", default=None)
            if not vk_token and not os.getenv("VK_ACCESS_TOKEN"):
                raise ValueError(
                    "Для продакшена требуется VK API токен. "
                    "Установите его в local.yaml или переменной окружения VK_ACCESS_TOKEN"
                )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получает значение из конфигурации по ключу.
        
        Args:
            key: Ключ конфигурации (например, 'logging.level')
            default: Значение по умолчанию
            
        Returns:
            Значение из конфигурации
        """
        if not self.config:
            self.load_config()
        
        return OmegaConf.select(self.config, key, default=default)
    
    def update(self, key: str, value: Any) -> None:
        """
        Обновляет значение в конфигурации.
        
        Args:
            key: Ключ конфигурации
            value: Новое значение
        """
        if not self.config:
            self.load_config()
        
        OmegaConf.update(self.config, key, value)
    
    def save_local_config(self, data: Dict[str, Any]) -> None:
        """
        Сохраняет локальную конфигурацию.
        
        Args:
            data: Данные для сохранения
        """
        local_config_path = self.config_dir / "local.yaml"
        
        if local_config_path.exists():
            existing = OmegaConf.load(str(local_config_path))
            merged = OmegaConf.merge(existing, data)
        else:
            merged = OmegaConf.create(data)
        
        OmegaConf.save(merged, local_config_path)
        
        self.load_config()
    
    def print_config(self, show_sensitive: bool = False) -> None:
        """
        Выводит текущую конфигурацию.
        
        Args:
            show_sensitive: Показывать ли чувствительные данные (токены)
        """
        if not self.config:
            self.load_config()
        
        print(f"\n{'='*50}")
        print(f"Конфигурация приложения (режим: {self.env})")
        print(f"{'='*50}")
        
        config_copy = OmegaConf.to_container(self.config, resolve=True)
        
        if not show_sensitive:
            self._hide_sensitive_data(config_copy)
        
        import yaml
        print(yaml.dump(config_copy, default_flow_style=False, allow_unicode=True))
    
    def _hide_sensitive_data(self, config: Dict) -> None:
        """
        Скрывает чувствительные данные в конфигурации.
        
        Args:
            config: Конфигурация для обработки
        """
        if isinstance(config, dict):
            if "vk" in config and isinstance(config["vk"], dict):
                if "access_token" in config["vk"] and config["vk"]["access_token"]:
                    token = config["vk"]["access_token"]
                    config["vk"]["access_token"] = f"{token[:10]}...{token[-5:]}"


_config_manager: Optional[ConfigManager] = None


def get_config(env: Optional[str] = None) -> DictConfig:
    """
    Получает глобальную конфигурацию.
    
    Args:
        env: Режим работы (опционально)
        
    Returns:
        Объект конфигурации
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(env=env)
    
    return _config_manager.load_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Получает значение из глобальной конфигурации.
    
    Args:
        key: Ключ конфигурации
        default: Значение по умолчанию
        
    Returns:
        Значение из конфигурации
    """
    config = get_config()
    return OmegaConf.select(config, key, default=default)