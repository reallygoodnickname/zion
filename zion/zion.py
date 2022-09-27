import database
import configparser
import logging

from flask import Flask

from admin.index import admin_index
from admin.security import admin_security
from admin.settings import admin_settings

from index import index
from login import login
from logout import logout

CONFIG_PATH = 'zion.ini'
LOG_PATH = 'logs/zion.log'

# Setting up logging
logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt="%Y-%d-%m %H:%M:%S",
                    filename=LOG_PATH,
                    encoding='utf-8',
                    level=logging.WARNING)

app = Flask(__name__)

# Adding some blueprints
app.register_blueprint(admin_index)
app.register_blueprint(admin_security)
app.register_blueprint(admin_settings)

app.register_blueprint(index)
app.register_blueprint(login)
app.register_blueprint(logout)

# Application secret key. Change it to something completely secret!
app.secret_key = b'dev'

# Getting configuration from config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

# Getting values from config file
db_user = config['database']['db_user']
db_pass = config['database']['db_pass']
db_host = config['database']['db_host']
db_name = config['database']['db_name']
# log_path = config['base']['log_path']

app.config["DATABASE"] = database.Database(db_host, db_user, db_pass, db_name)
app.config["ADMIN_MSG"] = None

app.run(debug=True)
