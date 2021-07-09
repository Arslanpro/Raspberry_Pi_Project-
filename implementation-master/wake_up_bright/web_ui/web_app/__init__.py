import os
from pathlib import Path
from threading import Thread

from flask import Flask


class WebUIThread(Thread):

    def __init__(self, host=None, port: int = None, debug=None, load_dotenv: bool = True, config=None):
        super().__init__()
        self.app = create_app(config=config)
        self.host = host
        self.port = port
        self.debug = debug
        self.load_dotenv = load_dotenv

    def run(self):
        self.app.run(self.host, self.port, self.debug, self.load_dotenv)


def create_app(config=None):
    """
    Flask app factory function. This function will return an app which is a fully functioning Flask web app.

    :param config: Parameter to choose a configuration. When not set, defaults to the development configuration.
    TODO: add more options for configuration.
    :return: Flask app instance.
    """
    # Figure out the instance directory path
    web_ui_dir = Path(__file__).parents[1]  # Returns the 2nd parent directory of this file (__init__.py)
    instance_dir = Path.joinpath(web_ui_dir, 'instance')  # Add the instance folder

    # Create the flask app with the specified /instance path and indicate the configuration can be found in /instance.
    app = Flask(__name__, instance_path=instance_dir, instance_relative_config=True)

    # Create the instance folder if it does not exist yet.
    try:
        os.makedirs(app.instance_path)  # Create an instance folder. TODO: Change the instance folder location.
    except OSError:
        pass  # If the folder already exists, do nothing.

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='development'  # This is the default key, it should be overridden in production with a secure key.
    )

    # Load configuration from passed in argument
    if config is not None:
        # app.config.from_mapping(config)
        # app.config.from_object(config)
        # app.config.from_pyfile(config)
        pass  # TODO: Add a correct way to import configuration such as any of the methods above.

    # Register all blueprints (routes)
    from wake_up_bright.web_ui.web_app.routes import bp
    app.register_blueprint(bp)

    # Return the app
    return app
