import logging
from flask import Flask
from .main import main
from config import Config
import json

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def create_app():
    logger.info("Creating Flask app")
    app = Flask(__name__)
    app.config.from_object(Config)
    
    logger.info("Registering main blueprint")
    app.register_blueprint(main)

    def json_format(value):
        return json.dumps(value, indent=2)

    app.jinja_env.filters['json_format'] = json_format

    @app.context_processor
    def inject_json_format():
        return dict(json_format=json_format)

    logger.info("App creation complete")
    return app