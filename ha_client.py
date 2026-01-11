"""Home Assistant API client with YAML file reading."""

import requests
import yaml
from pathlib import Path
from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)


class HomeAssistantClient:
    """Client for interacting with Home Assistant API."""

    def __init__(self):
        """Initialize client with configuration."""
        self.token = Config.HA_TOKEN
        self.base_url = None
        self._entity_names = {}  # Cache for entity_id -> friendly_name
        self._device_names = {}  # Cache for device_id -> device_name

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
        # Try to read automations from YAML file first
        yaml_path = Path(Config.AUTOMATIONS_YAML_PATH)
        if yaml_path.exists():
            logger.info(f"Reading automations from YAML file: {yaml_path}")

            # First, fetch entity and device names from HA API
            url = self._get_working_url()
            if url:
                self._fetch_entity_names(url)

            automations = self._read_automations_from_yaml(yaml_path)

            if automations:
                logger.info(f"Successfully loaded {len(automations)} automations from YAML")
                return automations
            else:
                logger.warning("No automations found in YAML file")
        else:
            logger.warning(f"YAML file not found at {yaml_path}")

        # Fallback: try REST API (will show limited info)
        url = self._get_working_url()
        if not url:
            logger.error("No working URL available for Home Assistant")
            return []

        logger.info("Falling back to REST API")
        return self._fetch_via_rest_api(url)

    def _read_automations_from_yaml(self, yaml_path):
        """
        Read automations from YAML file.

        Args:
            yaml_path (Path): Path to automations.yaml

        Returns:
            list: List of automation configurations
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                automations = yaml.safe_load(f)

            if not automations:
                logger.warning("YAML file is empty or invalid")
                return []

            logger.info(f"Loaded {len(automations)} automations from YAML file")

            # Process automations to match expected format
            processed = []
            for auto in automations:
                automation_id = auto.get('id', 'unknown')

                # Enrich triggers, conditions, and actions with friendly names
                triggers = self._enrich_with_names(
                    self._ensure_list(auto.get('triggers', auto.get('trigger', [])))
                )
                conditions = self._enrich_with_names(
                    self._ensure_list(auto.get('conditions', auto.get('condition', [])))
                )
                actions = self._enrich_with_names(
                    self._ensure_list(auto.get('actions', auto.get('action', [])))
                )

                processed_auto = {
                    'id': automation_id,
                    'alias': auto.get('alias', f'Automation {automation_id}'),
                    'entity_id': f"automation.{automation_id}",
                    'trigger': triggers,
                    'condition': conditions,
                    'action': actions
                }

                logger.debug(f"Loaded: {processed_auto['alias']} ({len(triggers)} triggers, {len(conditions)} conditions, {len(actions)} actions)")
                processed.append(processed_auto)

            return processed

        except Exception as e:
            logger.error(f"Error reading YAML file: {e}", exc_info=True)
            return []

    def _fetch_via_rest_api(self, url):
        """
        Fallback method to fetch automations via REST API.

        Args:
            url (str): Home Assistant URL

        Returns:
            list: List of automations with limited info
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{url}/api/states",
                headers=headers,
                timeout=5
            )

            if response.status_code != 200:
                return []

            states = response.json()
            automation_states = [
                s for s in states
                if s.get('entity_id', '').startswith('automation.')
                and s.get('state') == 'on'
            ]

            automations = []
            for state in automation_states:
                entity_id = state.get('entity_id', '')
                attributes = state.get('attributes', {})

                automations.append({
                    'alias': attributes.get('friendly_name', entity_id),
                    'entity_id': entity_id,
                    'trigger': [{
                        'platform': 'unknown',
                        'entity_id': 'Config not accessible - check YAML path'
                    }],
                    'condition': [],
                    'action': [{
                        'service': 'unknown'
                    }]
                })

            return automations

        except Exception as e:
            logger.error(f"Error fetching via REST API: {e}")
            return []

    def _fetch_entity_names(self, url):
        """
        Fetch all entity and device names from Home Assistant.

        Args:
            url (str): Home Assistant URL
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            logger.debug("Fetching entity names from Home Assistant API")

            # Get all states (contains entity_id -> friendly_name mapping)
            response = requests.get(
                f"{url}/api/states",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                states = response.json()
                logger.debug(f"Received {len(states)} states from API")

                for state in states:
                    entity_id = state.get('entity_id', '')
                    attributes = state.get('attributes', {})
                    friendly_name = attributes.get('friendly_name', entity_id)

                    if entity_id:
                        self._entity_names[entity_id] = friendly_name
                        logger.debug(f"Mapped: {entity_id} -> {friendly_name}")

                logger.info(f"Cached {len(self._entity_names)} entity names")
            else:
                logger.warning(f"Failed to fetch entity names: HTTP {response.status_code}")

        except Exception as e:
            logger.warning(f"Error fetching entity names: {e}")

    def _enrich_with_names(self, items):
        """
        Enrich triggers/conditions/actions with friendly names.

        Args:
            items (list): List of trigger/condition/action dicts

        Returns:
            list: Enriched items
        """
        enriched = []

        for item in items:
            if not isinstance(item, dict):
                enriched.append(item)
                continue

            # Create a copy to avoid modifying original
            enriched_item = item.copy()

            # Add friendly name for entity_id
            entity_id = item.get('entity_id')
            if entity_id:
                logger.debug(f"Looking up entity_id: {entity_id}")
                if entity_id in self._entity_names:
                    friendly = self._entity_names[entity_id]
                    enriched_item['_friendly_name'] = friendly
                    logger.debug(f"  Found friendly name: {friendly}")
                else:
                    logger.debug(f"  No friendly name found for {entity_id}")

            # Handle targets (can have entity_id inside)
            target = item.get('target', {})
            if isinstance(target, dict) and 'entity_id' in target:
                target_entity = target['entity_id']
                logger.debug(f"Looking up target entity_id: {target_entity}")
                if target_entity in self._entity_names:
                    friendly = self._entity_names[target_entity]
                    enriched_item['_target_friendly_name'] = friendly
                    logger.debug(f"  Found target friendly name: {friendly}")
                else:
                    logger.debug(f"  No friendly name found for target {target_entity}")

            enriched.append(enriched_item)

        return enriched

    def _ensure_list(self, item):
        """
        Convert item to list if it isn't already.

        Args:
            item: Item to convert

        Returns:
            list: Item as list
        """
        if isinstance(item, list):
            return item
        elif item:
            return [item]
        else:
            return []