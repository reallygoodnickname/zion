import database
import click
import configparser
import logging
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   Flask)

app = Flask(__name__)

CONFIG_PATH = 'zion.ini'
LOG_PATH = 'logs/zion.log'


# Getting configuration from config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)


# Getting values from config file
db_user = config['database']['db_user']
db_pass = config['database']['db_pass']
db_host = config['database']['db_host']
db_name = config['database']['db_name']
# log_path = config['base']['log_path']

# try:
#    open(log_path, 'rw').close()
# except PermissionError:
#    print("Couldn't open log file, check your permissions!")

# Setting up logging
logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt="%Y-%d-%m %H:%M:%S",
                    filename=LOG_PATH,
                    encoding='utf-8')


db = database.Database(db_host, db_user, db_pass, db_name)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: add username badchars check
        if (db.validateUser(request.form['username'],
                            request.form['password'])):
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))

    return render_template('login.html')


# @app.route("/register")
# def register():
#     pass


