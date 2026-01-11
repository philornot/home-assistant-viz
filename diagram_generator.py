"""Flowchart diagram generation using Graphviz."""

from graphviz import Digraph
from logger_config import setup_logger

logger = setup_logger(__name__)


class DiagramGenerator:
    """Generate flowchart diagrams from automation configurations."""

    COLORS = {
        'automation': '#4a90e2',
        'trigger': '#50c878',
        'condition': '#ff9f43',
        'action': '#ee5a6f',
        'background': '#1e1e1e'
    }

    def create_flowchart(self, automations):
        """
        Create flowchart diagram from automations.

        Args:
            automations (list): List of automation configurations

        Returns:
            str: SVG representation of the flowchart
        """
        logger.info(f"Generating flowchart for {len(automations)} automations")

        dot = Digraph(comment='HA Automations', format='svg')
        dot.attr(rankdir='TB', bgcolor=self.COLORS['background'])
        dot.attr('node', style='filled', fontname='Arial', fontcolor='white')
        dot.attr('edge', color='white', fontcolor='white', fontname='Arial')

        for idx, automation in enumerate(automations):
            self._process_automation(dot, idx, automation)

        svg = dot.pipe(encoding='utf-8')
        logger.debug("Flowchart generated successfully")
        return svg

    def _process_automation(self, dot, idx, automation):
        """
        Process single automation and add to diagram.

        Args:
            dot: Graphviz Digraph object
            idx (int): Automation index
            automation (dict): Automation configuration
        """
        auto_id = f"auto_{idx}"
        name = automation.get("alias", f"Automation {idx}")

        # Automation name node
        dot.node(
            auto_id,
            name,
            shape='box',
            style='rounded,filled',
            fillcolor=self.COLORS['automation']
        )

        # Process triggers
        triggers = self._ensure_list(automation.get("trigger", []))
        last_node = self._add_triggers(dot, auto_id, triggers)

        # Process conditions
        conditions = self._ensure_list(automation.get("condition", []))
        if conditions:
            last_node = self._add_conditions(dot, auto_id, conditions, last_node)

        # Process actions
        actions = self._ensure_list(automation.get("action", []))
        self._add_actions(dot, auto_id, actions, last_node, bool(conditions))

    def _ensure_list(self, item):
        """Convert item to list if it isn't already."""
        return item if isinstance(item, list) else [item] if item else []

    def _add_triggers(self, dot, auto_id, triggers):
        """Add trigger nodes to diagram."""
        if not triggers:
            return auto_id

        for t_idx, trigger in enumerate(triggers):
            trigger_id = f"{auto_id}_trigger_{t_idx}"

            # Handle different trigger formats
            if isinstance(trigger, dict):
                trigger_type = trigger.get("platform", "unknown")
                label = f"Trigger: {trigger_type}"

                if "entity_id" in trigger:
                    label += f"\n{trigger['entity_id']}"
            elif isinstance(trigger, str):
                # Trigger is just a string (timestamp or simple value)
                label = f"Trigger: {trigger[:30]}"  # Limit length
            else:
                label = f"Trigger: {type(trigger).__name__}"

            dot.node(
                trigger_id,
                label,
                shape='parallelogram',
                fillcolor=self.COLORS['trigger']
            )
            dot.edge(auto_id, trigger_id)

        return f"{auto_id}_trigger_{len(triggers)-1}" if triggers else auto_id

    def _add_conditions(self, dot, auto_id, conditions, last_node):
        """Add condition nodes to diagram."""
        if not conditions:
            return last_node

        for c_idx, condition in enumerate(conditions):
            condition_id = f"{auto_id}_condition_{c_idx}"

            # Handle different condition formats
            if isinstance(condition, dict):
                condition_type = condition.get("condition", "unknown")
                label = f"Condition: {condition_type}"
            elif isinstance(condition, str):
                label = f"Condition: {condition[:30]}"
            else:
                label = f"Condition: {type(condition).__name__}"

            dot.node(
                condition_id,
                label,
                shape='diamond',
                fillcolor=self.COLORS['condition']
            )
            dot.edge(last_node, condition_id)

        return f"{auto_id}_condition_{len(conditions)-1}"

    def _add_actions(self, dot, auto_id, actions, last_node, has_conditions):
        """Add action nodes to diagram."""
        if not actions:
            return

        for a_idx, action in enumerate(actions):
            action_id = f"{auto_id}_action_{a_idx}"

            # Handle different action formats
            if isinstance(action, dict):
                action_type = action.get("service", action.get("action", "unknown"))
                label = f"Action: {action_type}"
            elif isinstance(action, str):
                label = f"Action: {action[:30]}"
            else:
                label = f"Action: {type(action).__name__}"

            dot.node(
                action_id,
                label,
                shape='box',
                fillcolor=self.COLORS['action']
            )

            edge_label = "yes" if has_conditions else ""
            dot.edge(last_node, action_id, label=edge_label)