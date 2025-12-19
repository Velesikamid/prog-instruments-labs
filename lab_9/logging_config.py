import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from config_manager import get_config_value


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: Optional[bool] = None,
    log_dir: Optional[str] = None
) -> None:
    """
    Настройка логирования для всего приложения.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Если True, логи будут записываться в файл
        log_dir: Директория для логов
    """
    try:
        config_level = get_config_value("logging.level", "INFO")
        config_to_file = get_config_value("logging.to_file", True)
        config_dir = get_config_value("logging.dir", "logs")
        config_format = get_config_value("logging.format", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        config_date_format = get_config_value("logging.date_format", "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        config_level = "INFO"
        config_to_file = True
        config_dir = "logs"
        config_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        config_date_format = "%Y-%m-%d %H:%M:%S"
    
    log_level = log_level or config_level
    log_to_file = log_to_file if log_to_file is not None else config_to_file
    log_dir = Path(log_dir or config_dir)
    
    log_dir.mkdir(exist_ok=True, parents=True)
    
    formatter = logging.Formatter(
        fmt=config_format,
        datefmt=config_date_format
    )
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    logger.handlers.clear()
    
    console_enabled = get_config_value("logging.console", True)
    if console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        logger.addHandler(console_handler)
    
    if log_to_file:
        file_format = get_config_value("logging.file_format", "app_%Y%m%d_%H%M%S.log")
        log_filename = log_dir / datetime.now().strftime(file_format)
        file_handler = logging.FileHandler(str(log_filename), encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    
    try:
        perf_mode = get_config_value("prod.performance_mode", False)
    except:
        perf_mode = False
        
    if perf_mode:
        try:
            from logging.handlers import RotatingFileHandler
            max_size = get_config_value("logging.max_file_size", "10MB")
            backup_count = get_config_value("logging.backup_count", 5)
            
            if max_size.endswith("MB"):
                max_bytes = int(max_size[:-2]) * 1024 * 1024
            elif max_size.endswith("KB"):
                max_bytes = int(max_size[:-2]) * 1024
            else:
                max_bytes = 10 * 1024 * 1024
            
            rotating_handler = RotatingFileHandler(
                str(log_filename),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            rotating_handler.setFormatter(formatter)
            rotating_handler.setLevel(logging.DEBUG)
            logger.addHandler(rotating_handler)
            
        except ImportError:
            pass
    
    logger.info(f"Логирование инициализировано. Уровень: {log_level}")