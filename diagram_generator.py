"""HTML diagram generation for automation workflows."""

from logger_config import setup_logger

logger = setup_logger(__name__)


class DiagramGenerator:
    """Generate HTML diagrams from automation configurations."""

    def create_flowchart(self, automations):
        """
        Create HTML flowchart from automations.

        Args:
            automations (list): List of automation configurations

        Returns:
            str: HTML representation of the flowcharts
        """
        logger.info(f"Generating HTML diagrams for {len(automations)} automations")

        html_parts = ['<div class="diagrams-container">']

        for idx, automation in enumerate(automations):
            html_parts.append(self._create_automation_diagram(idx, automation))

        html_parts.append('</div>')

        html = ''.join(html_parts)
        logger.debug("HTML diagrams generated successfully")
        return html

    def _create_automation_diagram(self, idx, automation):
        """
        Create HTML diagram for single automation.

        Args:
            idx (int): Automation index
            automation (dict): Automation configuration

        Returns:
            str: HTML for single automation diagram
        """
        name = automation.get("alias", f"Automation {idx}")
        triggers = self._ensure_list(automation.get("trigger", []))
        conditions = self._ensure_list(automation.get("condition", []))
        actions = self._ensure_list(automation.get("action", []))

        html = f'''
        <div class="automation-flow">
            <div class="flow-header">
                <h3 class="automation-name">{self._escape_html(name)}</h3>
            </div>
            <div class="flow-body">
        '''

        # Add triggers
        if triggers:
            html += '<div class="flow-section">'
            html += '<h4 class="section-label">Triggers</h4>'
            html += '<div class="flow-items">'
            for trigger in triggers:
                html += self._create_trigger_node(trigger)
            html += '</div></div>'
            html += '<div class="flow-arrow">↓</div>'

        # Add conditions
        if conditions:
            html += '<div class="flow-section">'
            html += '<h4 class="section-label">Conditions</h4>'
            html += '<div class="flow-items">'
            for condition in conditions:
                html += self._create_condition_node(condition)
            html += '</div></div>'
            html += '<div class="flow-arrow">↓ yes</div>'

        # Add actions
        if actions:
            html += '<div class="flow-section">'
            html += '<h4 class="section-label">Actions</h4>'
            html += '<div class="flow-items">'
            for action in actions:
                html += self._create_action_node(action)
            html += '</div></div>'

        html += '''
            </div>
        </div>
        '''

        return html

    def _create_trigger_node(self, trigger):
        """
        Create HTML for trigger node.

        Args:
            trigger: Trigger configuration

        Returns:
            str: HTML for trigger node
        """
        if isinstance(trigger, dict):
            trigger_type = trigger.get("platform", trigger.get("trigger", "unknown"))
            entity_id = trigger.get("entity_id", "")
            friendly_name = trigger.get("_friendly_name", "")

            # Build detailed label based on trigger type
            if trigger_type == "state":
                to_state = trigger.get("to", "")
                from_state = trigger.get("from", "")
                if to_state or from_state:
                    label = f"State: {from_state or 'any'} → {to_state or 'any'}"
                else:
                    label = "State change"
            elif trigger_type == "time":
                at_time = trigger.get("at", "")
                label = f"Time: {at_time}" if at_time else "Time trigger"
            elif trigger_type == "numeric_state":
                above = trigger.get("above", "")
                below = trigger.get("below", "")
                label = f"Numeric: "
                if above:
                    label += f"> {above}"
                if below:
                    label += f" < {below}" if above else f"< {below}"
            elif trigger_type == "sun":
                event = trigger.get("event", "")
                label = f"Sun: {event}" if event else "Sun trigger"
            elif trigger_type == "webhook":
                webhook_id = trigger.get("webhook_id", "")
                label = f"Webhook: {webhook_id}" if webhook_id else "Webhook trigger"
            elif trigger_type == "mqtt":
                topic = trigger.get("topic", "")
                label = f"MQTT: {topic}" if topic else "MQTT trigger"
            elif trigger_type == "event":
                event_type = trigger.get("event_type", "")
                label = f"Event: {event_type}" if event_type else "Event trigger"
            elif trigger_type == "zone":
                zone = trigger.get("zone", "")
                event = trigger.get("event", "")
                label = f"Zone: {event or 'change'}"
                if zone:
                    label += f" ({zone})"
            elif trigger_type == "conversation":
                command = trigger.get("command", "")
                if isinstance(command, list):
                    command = ", ".join(command[:2])  # Show first 2 commands
                label = f"Conversation: {command}" if command else "Conversation trigger"
            elif trigger_type == "device":
                device_type = trigger.get("type", "")
                label = f"Device: {device_type}" if device_type else "Device trigger"
            elif trigger_type == "time_pattern":
                label = "Time pattern"
            else:
                label = f"{trigger_type}"

            # Use friendly name if available, otherwise entity_id
            sublabel_text = friendly_name or entity_id
            sublabel = f"<div class='node-sublabel'>{self._escape_html(sublabel_text)}</div>" if sublabel_text else ""
        elif isinstance(trigger, str):
            label = self._truncate(trigger, 30)
            sublabel = ""
        else:
            label = type(trigger).__name__
            sublabel = ""

        return f'''
        <div class="flow-node trigger-node">
            <div class="node-icon">▶</div>
            <div class="node-content">
                <div class="node-label">{self._escape_html(label)}</div>
                {sublabel}
            </div>
        </div>
        '''

    def _create_condition_node(self, condition):
        """
        Create HTML for condition node.

        Args:
            condition: Condition configuration

        Returns:
            str: HTML for condition node
        """
        if isinstance(condition, dict):
            condition_type = condition.get("condition", condition.get("type", "unknown"))
            entity_id = condition.get("entity_id", "")
            friendly_name = condition.get("_friendly_name", "")

            # Build detailed label based on condition type
            if condition_type == "state":
                state = condition.get("state", "")
                label = f"State = {state}" if state else "State condition"
            elif condition_type == "numeric_state":
                above = condition.get("above", "")
                below = condition.get("below", "")
                label = f"Numeric: "
                if above:
                    label += f"> {above}"
                if below:
                    label += f" < {below}" if above else f"< {below}"
            elif condition_type == "time":
                after = condition.get("after", "")
                before = condition.get("before", "")
                weekday = condition.get("weekday", [])
                if weekday:
                    days = ", ".join(weekday) if isinstance(weekday, list) else weekday
                    label = f"Time: {days}"
                elif after or before:
                    label = f"Time: {after or ''} - {before or ''}"
                else:
                    label = "Time condition"
            elif condition_type == "sun":
                after = condition.get("after", "")
                before = condition.get("before", "")
                label = f"Sun: {after or ''} to {before or ''}" if (after or before) else "Sun condition"
            elif condition_type == "zone":
                zone = condition.get("zone", "")
                label = f"Zone: {zone}" if zone else "Zone condition"
            elif condition_type == "template":
                label = "Template condition"
            elif condition_type == "and":
                label = "AND condition"
            elif condition_type == "or":
                label = "OR condition"
            elif condition_type == "not":
                label = "NOT condition"
            elif condition_type == "device":
                label = "Device condition"
            else:
                label = condition_type

            # Use friendly name if available, otherwise entity_id
            sublabel_text = friendly_name or entity_id
            sublabel = f"<div class='node-sublabel'>{self._escape_html(sublabel_text)}</div>" if sublabel_text else ""
        elif isinstance(condition, str):
            label = self._truncate(condition, 30)
            sublabel = ""
        else:
            label = type(condition).__name__
            sublabel = ""

        return f'''
        <div class="flow-node condition-node">
            <div class="node-icon">◆</div>
            <div class="node-content">
                <div class="node-label">{self._escape_html(label)}</div>
                {sublabel}
            </div>
        </div>
        '''

    def _create_action_node(self, action):
        """
        Create HTML for action node.

        Args:
            action: Action configuration

        Returns:
            str: HTML for action node
        """
        if isinstance(action, dict):
            # Try different keys for action service
            action_service = (action.get("service") or
                              action.get("action") or
                              action.get("event", ""))

            friendly_name = action.get("_target_friendly_name", "")
            action_alias = action.get("alias", "")

            # Handle special action types
            if "delay" in action:
                delay = action.get("delay", "")
                label = f"Delay: {delay}"
            elif "wait_template" in action:
                label = "Wait for template"
            elif "wait_for_trigger" in action:
                label = "Wait for trigger"
            elif "choose" in action:
                label = "Choose action"
            elif "repeat" in action:
                label = "Repeat action"
            elif "if" in action:
                label = "If condition"
            elif action_alias:
                # Use the alias if provided (from YAML)
                label = action_alias
            elif action_service:
                # Parse service name for better display
                if "." in action_service:
                    domain, service = action_service.split(".", 1)
                    label = f"{domain}: {service.replace('_', ' ').title()}"
                else:
                    label = action_service.replace('_', ' ').title()
            elif action.get("type"):
                # Device action
                action_type = action.get("type", "")
                label = f"Device: {action_type.replace('_', ' ').title()}"
            else:
                label = "Action"

            # Get entity_id or target for sublabel
            entity_id = action.get("entity_id", "")
            target = action.get("target", {})

            if not entity_id and isinstance(target, dict):
                entity_id = target.get("entity_id", "")
                # Check for area_id or label_id
                if not entity_id:
                    area_id = target.get("area_id", "")
                    label_id = target.get("label_id", "")
                    if area_id:
                        if isinstance(area_id, list):
                            entity_id = f"Areas: {', '.join(area_id)}"
                        else:
                            entity_id = f"Area: {area_id}"
                    elif label_id:
                        if isinstance(label_id, list):
                            entity_id = f"Labels: {', '.join(label_id)}"
                        else:
                            entity_id = f"Label: {label_id}"

            # Use friendly name if available
            sublabel_text = friendly_name or entity_id
            sublabel = f"<div class='node-sublabel'>{self._escape_html(sublabel_text)}</div>" if sublabel_text else ""
        elif isinstance(action, str):
            label = self._truncate(action, 30)
            sublabel = ""
        else:
            label = type(action).__name__
            sublabel = ""

        return f'''
        <div class="flow-node action-node">
            <div class="node-icon">●</div>
            <div class="node-content">
                <div class="node-label">{self._escape_html(label)}</div>
                {sublabel}
            </div>
        </div>
        '''

    def _ensure_list(self, item):
        """
        Convert item to list if it isn't already.

        Args:
            item: Item to convert

        Returns:
            list: Item as list
        """
        return item if isinstance(item, list) else [item] if item else []

    def _truncate(self, text, max_length):
        """
        Truncate text to max length.

        Args:
            text (str): Text to truncate
            max_length (int): Maximum length

        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + '...'

    def _escape_html(self, text):
        """
        Escape HTML special characters.

        Args:
            text (str): Text to escape

        Returns:
            str: Escaped text
        """
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
