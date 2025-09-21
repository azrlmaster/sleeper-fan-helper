from flask import Flask
import os

def create_app():
    """
    Application factory for the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the main blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
