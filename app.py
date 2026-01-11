"""Main Flask application."""

from flask import Flask, render_template, jsonify
from config import Config
from ha_client import HomeAssistantClient
from diagram_generator import DiagramGenerator
from logger_config import setup_logger

logger = setup_logger(__name__)
app = Flask(__name__)

ha_client = HomeAssistantClient()
diagram_gen = DiagramGenerator()


@app.route('/')
def index():
    """Render main page."""
    logger.debug("Serving index page")
    return render_template('index.html', refresh_interval=Config.REFRESH_INTERVAL)


@app.route('/api/diagram')
def get_diagram():
    """
    API endpoint to fetch current automation diagram.

    Returns:
        JSON response with SVG content or error
    """
    logger.debug("Diagram API called")

    automations = ha_client.fetch_automations()

    if not automations:
        return jsonify({
            'success': False,
            'message': 'No automations found or cannot connect to Home Assistant'
        })

    svg_content = diagram_gen.create_flowchart(automations)
    return jsonify({
        'success': True,
        'svg': svg_content,
        'count': len(automations)
    })


if __name__ == '__main__':
    if not Config.HA_TOKEN:
        logger.warning("HA_TOKEN environment variable not set!")
        logger.warning("Set it with: export HA_TOKEN='your_token_here'")

    logger.info(f"Starting server on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG)