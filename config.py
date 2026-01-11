"""Configuration settings for the application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration with fallback support."""

    # Home Assistant connection
    HA_IPS = [
        os.getenv("HA_IP_PRIMARY", "192.168.1.221"),
        os.getenv("HA_IP_FALLBACK", "192.168.1.225")
    ]
    HA_PORT = int(os.getenv("HA_PORT", "8123"))
    HA_TOKEN = os.getenv("HA_TOKEN", "")

    # Path to automations.yaml file
    AUTOMATIONS_YAML_PATH = os.getenv(
        "AUTOMATIONS_YAML_PATH",
        "/opt/homeassistant/automations.yaml"
    )

    # Flask settings
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Refresh interval (seconds)
    REFRESH_INTERVAL = 30

    # Logging
    LOG_FILE = "ha_automation_viz.log"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5