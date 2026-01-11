"""Home Assistant API client with connection fallback."""

import requests
from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant API."""

    def __init__(self):
        """Initialize client with configuration."""
        self.token = Config.HA_TOKEN
        self.base_url = None

    def _get_working_url(self):
        """
        Test connection to Home Assistant using fallback IPs.

        Returns:
            str: Working base URL or None if all fail
        """
        if self.base_url:
            return self.base_url

        for ip in Config.HA_IPS:
            url = f"http://{ip}:{Config.HA_PORT}"
            try:
                response = requests.get(
                    f"{url}/api/",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=2
                )
                if response.status_code == 200:
                    logger.info(f"Connected to Home Assistant at {url}")
                    self.base_url = url
                    return url
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to connect to {url}: {e}")
                continue

        logger.error("Cannot connect to Home Assistant on any IP")
        return None

    def fetch_automations(self):
        """
        Fetch all enabled automations from Home Assistant.

        Returns:
            list: List of automation configurations
        """
        url = self._get_working_url()
        if not url:
            return []

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            # First, try to get automations via states API
            response = requests.get(
                f"{url}/api/states",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                states = response.json()
                # Filter for automation entities
                automations = [
                    s for s in states
                    if s.get('entity_id', '').startswith('automation.')
                    and s.get('state') == 'on'
                ]
                logger.info(f"Fetched {len(automations)} enabled automations from states")

                # Get detailed automation configs
                detailed_automations = []
                for auto in automations:
                    entity_id = auto['entity_id']
                    # Try to get automation config
                    config_response = requests.get(
                        f"{url}/api/config/automation/config/{entity_id}",
                        headers=headers,
                        timeout=3
                    )
                    if config_response.status_code == 200:
                        detailed_automations.append(config_response.json())
                    else:
                        # Fallback to using attributes from state
                        detailed_automations.append({
                            'alias': auto['attributes'].get('friendly_name', entity_id),
                            'trigger': auto['attributes'].get('last_triggered', []),
                            'action': [{'service': 'unknown'}]
                        })

                return detailed_automations
            else:
                logger.error(f"Error fetching automations: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Exception while fetching automations: {e}")
            return []