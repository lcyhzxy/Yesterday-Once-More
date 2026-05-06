"""
Time Revival - AI Photo Video Generation System
Configuration Module

Handles environment configuration and application settings.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    # Flask settings
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = False
    FLASK_THREADED: bool = True

    # API settings
    API_PREFIX: str = "/api"
    MAX_CONTENT_LENGTH: int = 50 * 1024 * 1024  # 50MB max upload

    # Video generation defaults
    DEFAULT_DURATION: int = 5
    DEFAULT_FPS: int = 30
    DEFAULT_RESOLUTION: Tuple[int, int] = (1280, 720)
    DEFAULT_MOTION_MODE: str = "breathing"
    DEFAULT_STYLE: str = "warm_memories"
    DEFAULT_INTENSITY: float = 0.5

    # Video generation limits
    MAX_DURATION: int = 30  # seconds
    MIN_DURATION: int = 1
    MAX_FPS: int = 60
    MIN_FPS: int = 15
    MAX_RESOLUTION: Tuple[int, int] = (1920, 1080)
    MIN_RESOLUTION: Tuple[int, int] = (640, 480)

    # File paths
    BASE_DIR: Path = Path(__file__).parent.resolve()
    UPLOAD_DIR: Path = None
    OUTPUT_DIR: Path = None
    TEMP_DIR: Path = None

    # Supported formats
    SUPPORTED_IMAGE_FORMATS: Tuple[str, ...] = ("jpg", "jpeg", "png", "webp", "bmp")
    SUPPORTED_VIDEO_FORMATS: Tuple[str, ...] = ("mp4", "avi", "mov")

    # Task settings
    TASK_TIMEOUT: int = 300  # seconds
    TASK_CLEANUP_INTERVAL: int = 3600  # seconds
    TASK_MAX_AGE: int = 86400  # 24 hours

    # CORS settings
    CORS_ENABLED: bool = True
    CORS_ORIGINS: str = "*"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    def __post_init__(self):
        """Initialize dynamic paths after dataclass initialization."""
        if self.UPLOAD_DIR is None:
            self.UPLOAD_DIR = self.BASE_DIR / "uploads"
        if self.OUTPUT_DIR is None:
            self.OUTPUT_DIR = self.BASE_DIR / "output"
        if self.TEMP_DIR is None:
            self.TEMP_DIR = self.BASE_DIR / "temp"

        # Ensure directories exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "Config":
        """
        Create configuration from environment variables.

        Returns:
            Config instance with values from environment
        """
        config = cls()

        # Flask settings
        config.FLASK_HOST = os.getenv("FLASK_HOST", config.FLASK_HOST)
        config.FLASK_PORT = int(os.getenv("FLASK_PORT", config.FLASK_PORT))
        config.FLASK_DEBUG = os.getenv("FLASK_DEBUG", str(config.FLASK_DEBUG)).lower() == "true"

        # API settings
        config.API_PREFIX = os.getenv("API_PREFIX", config.API_PREFIX)

        # Video defaults
        config.DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", config.DEFAULT_DURATION))
        config.DEFAULT_FPS = int(os.getenv("DEFAULT_FPS", config.DEFAULT_FPS))
        config.DEFAULT_MOTION_MODE = os.getenv("DEFAULT_MOTION_MODE", config.DEFAULT_MOTION_MODE)
        config.DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", config.DEFAULT_STYLE)
        config.DEFAULT_INTENSITY = float(os.getenv("DEFAULT_INTENSITY", config.DEFAULT_INTENSITY))

        # Custom paths
        upload_dir = os.getenv("UPLOAD_DIR")
        if upload_dir:
            config.UPLOAD_DIR = Path(upload_dir)
        output_dir = os.getenv("OUTPUT_DIR")
        if output_dir:
            config.OUTPUT_DIR = Path(output_dir)
        temp_dir = os.getenv("TEMP_DIR")
        if temp_dir:
            config.TEMP_DIR = Path(temp_dir)

        # CORS settings
        config.CORS_ENABLED = os.getenv("CORS_ENABLED", str(config.CORS_ENABLED)).lower() == "true"
        config.CORS_ORIGINS = os.getenv("CORS_ORIGINS", config.CORS_ORIGINS)

        # Rate limiting
        config.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", str(config.RATE_LIMIT_ENABLED)).lower() == "true"

        return config


def get_config() -> Config:
    """
    Get application configuration.

    Returns:
        Config instance
    """
    return Config.from_env()


# Global config instance
config = get_config()
