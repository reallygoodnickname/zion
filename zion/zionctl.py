from . import SETTINGS, CONFIG_PATH
from .zion import app

from .mailer import Mailer
from .database import Database

from .models.users import users
from .models.posts import posts
from .models.settings import settings
from .models.comments import comments

from flask import request, redirect, url_for
from waitress import serve

from os import environ
import configparser
import click


@click.command()
@click.option('--host', default='0.0.0.0',  # nosec
              help='Hostname to bind to')
@click.option('--port', default='8080',
              help='Port to bind to')
@click.option('-c', '--config', default=CONFIG_PATH,
              help='Path to config file')
def run(host, port, config):
    app.config["CONFIG_PATH"] = config

    creds = dict()

    # Parse creds from environment
    try:
        for entry in ["db_user", "db_pass", "db_host", "db_name"]:
            creds[entry] = environ["ZION_"+entry.upper()]

    except KeyError:
        # Getting configuration from config file
        conf = configparser.ConfigParser()
        conf.read(app.config["CONFIG_PATH"])

        # Getting values from config file
        try:
            for entry in ["db_user", "db_pass", "db_host", "db_name"]:
                creds[entry] = conf['database'][entry]
        except KeyError:
            app.logger.critical(
                "Failed to parse config file. You're missing some entries!")
            exit(1)

    # Get database
    db = Database(host=creds["db_host"], user=creds["db_user"],
                  passwd=creds["db_pass"], name=creds["db_name"])

    # Safe objects to config
    app.config["CONFIGURED"] = db.configured
    app.config["DATABASE"] = db
    app.config["USERS"] = users(db)
    app.config["POSTS"] = posts(db)
    app.config["SETTINGS"] = settings(db)
    app.config["COMMENTS"] = comments(db)

    settings_obj = app.config["SETTINGS"]

    # Set configuration if app is launched first time
    def _redirect_config():
        # Add static to whitelist so css files can be accessed
        if (not app.config["CONFIGURED"] and
                request.endpoint not in ["config.configure",
                                         "static"]):
            return redirect(url_for("config.configure"))

    if not app.config["CONFIGURED"]:
        # Import config and register it
        from .views.configure import config
        app.register_blueprint(config)

        # Run function before request
        app.before_request(_redirect_config)

        # Add all settings to database
        for setting in SETTINGS:
            settings_obj.add_setting(setting_name=setting,
                                     setting_value=SETTINGS[setting][0],
                                     setting_desc=SETTINGS[setting][1],
                                     setting_type=SETTINGS[setting][2])

    settings_ = settings_obj.get_settings()

    # Get secret key from db
    if app.config["CONFIGURED"]:
        app.secret_key = settings_["SECRET_KEY"]

    for setting in settings_:
        if setting == "SECRET_KEY" and settings_["SECRET_KEY"][0] is None:
            continue
        # Translate 1 and 0 to true and false
        if settings_[setting][0] in ["1", "0"]:
            app.config[setting] = bool(int(settings_[setting][0]))
            settings_[setting][0] = app.config[setting]
        else:
            app.config[setting] = settings_[setting][0]
            settings_[setting][0] = app.config[setting]

        # Save all settings so they can be accessed from anywhere
    app.config["ZION_SETTINGS"] = settings_

    # Enable SMTP if "SMTP_ENABLED" is True
    if app.config["SMTP_ENABLED"]:
        if ":" not in app.config["SMTP_HOSTNAME"]:
            app.config["MAILER"] = Mailer(app.config["SMTP_USERNAME"],
                                          app.config["SMTP_PASSWORD"],
                                          app.config["SMTP_HOSTNAME"],
                                          TLS=True)

        else:
            # Split hostname into host and post
            host_, port_ = app.config["SMTP_HOSTNAME"].split(":")

            # Create mailer object
            app.config["MAILER"] = Mailer(app.config["SMTP_USERNAME"],
                                          app.config["SMTP_PASSWORD"],
                                          host_, port_, TLS=True)

    # app.run(debug=True)
    serve(app, port=port, host=host)


if __name__ == "__main__":
    run()
