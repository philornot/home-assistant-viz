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
            logger.error("No working URL available for Home Assistant")
            return []

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            logger.debug("Fetching automation states from Home Assistant")
            response = requests.get(
                f"{url}/api/states",
                headers=headers,
                timeout=5
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch states: HTTP {response.status_code}")
                return []

            states = response.json()
            logger.debug(f"Received {len(states)} total states from Home Assistant")

            # Filter for automation entities that are enabled
            automation_states = [
                s for s in states
                if s.get('entity_id', '').startswith('automation.')
                and s.get('state') == 'on'
            ]
            logger.info(f"Found {len(automation_states)} enabled automations")

            if not automation_states:
                logger.warning("No enabled automations found in Home Assistant")
                return []

            # Convert state objects to automation configs
            detailed_automations = []
            for idx, auto_state in enumerate(automation_states):
                entity_id = auto_state.get('entity_id', 'unknown')
                attributes = auto_state.get('attributes', {})

                logger.debug(f"Processing automation {idx + 1}/{len(automation_states)}: {entity_id}")

                # Extract automation details from attributes
                automation_config = {
                    'alias': attributes.get('friendly_name', entity_id),
                    'entity_id': entity_id,
                    'trigger': self._extract_triggers(attributes),
                    'condition': self._extract_conditions(attributes),
                    'action': self._extract_actions(attributes)
                }

                logger.debug(f"  - Name: {automation_config['alias']}")
                logger.debug(f"  - Triggers: {len(automation_config['trigger'])} found")
                logger.debug(f"  - Conditions: {len(automation_config['condition'])} found")
                logger.debug(f"  - Actions: {len(automation_config['action'])} found")

                detailed_automations.append(automation_config)

            logger.info(f"Successfully processed {len(detailed_automations)} automations")
            return detailed_automations

        except requests.exceptions.Timeout:
            logger.error("Request to Home Assistant timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while fetching automations: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while fetching automations: {e}", exc_info=True)
            return []

    def _extract_triggers(self, attributes):
        """
        Extract trigger information from automation attributes.

        Args:
            attributes (dict): Automation attributes from HA state

        Returns:
            list: List of trigger configurations
        """
        # Try to get trigger from attributes
        triggers = []

        # Check if last_triggered exists as a hint that automation has triggers
        if 'last_triggered' in attributes:
            # Create a generic trigger representation
            triggers.append({
                'platform': 'state',
                'entity_id': attributes.get('entity_id', 'unknown')
            })

        # If no triggers found, add a placeholder
        if not triggers:
            triggers.append({
                'platform': 'unknown',
                'entity_id': ''
            })

        return triggers

    def _extract_conditions(self, attributes):
        """
        Extract condition information from automation attributes.

        Args:
            attributes (dict): Automation attributes from HA state

        Returns:
            list: List of condition configurations
        """
        # Home Assistant doesn't expose conditions in state attributes
        # Return empty list - conditions are optional
        return []

    def _extract_actions(self, attributes):
        """
        Extract action information from automation attributes.

        Args:
            attributes (dict): Automation attributes from HA state

        Returns:
            list: List of action configurations
        """
        actions = []

        # Try to infer action type from automation mode
        mode = attributes.get('mode', 'single')

        # Create a generic action representation
        actions.append({
            'service': 'automation.trigger',
            'mode': mode
        })

        return actions