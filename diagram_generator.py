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
            trigger_type = trigger.get("platform", "unknown")
            entity_id = trigger.get("entity_id", "")
            label = f"{trigger_type}"
            sublabel = f"<div class='node-sublabel'>{self._escape_html(entity_id)}</div>" if entity_id else ""
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
            condition_type = condition.get("condition", "unknown")
            label = condition_type
        elif isinstance(condition, str):
            label = self._truncate(condition, 30)
        else:
            label = type(condition).__name__

        return f'''
        <div class="flow-node condition-node">
            <div class="node-icon">◆</div>
            <div class="node-content">
                <div class="node-label">{self._escape_html(label)}</div>
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
            action_type = action.get("service", action.get("action", "unknown"))
            label = action_type
        elif isinstance(action, str):
            label = self._truncate(action, 30)
        else:
            label = type(action).__name__

        return f'''
        <div class="flow-node action-node">
            <div class="node-icon">●</div>
            <div class="node-content">
                <div class="node-label">{self._escape_html(label)}</div>
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
