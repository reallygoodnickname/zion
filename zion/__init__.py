from flask import Flask
from secrets import token_hex
from os import path

from logging.config import dictConfig

# Application version
version = '0.1.0'
__version__ = version

# Some application vars
BASE_PATH = path.dirname(__file__)
AVATAR_PATH = path.abspath(path.join(BASE_PATH, "static", "images"))

CONFIG_PATH = path.abspath(path.join(BASE_PATH, "zion.ini"))
LOG_PATH = path.abspath(path.join(BASE_PATH, "logs", "zion.log"))

# Settings used in application. Should not be edited!
SETTINGS = \
    {
        # OPTION_NAME    # VALUE # DESCRIPTION                     # TYPE
        "SMTP_ENABLED":  [False, "Enable mail support",            "checkbox"],
        "REQUIRE_MAIL":  [False, "Require mail for registration",  "checkbox"],
        "SMTP_HOSTNAME": ["",    "Mail server",                    "text"],
        "SMTP_USERNAME": ["",    "SMTP username",                  "text"],
        "SMTP_PASSWORD": ["",    "SMTP password",                  "text"],
        "ADMIN_ENABLED": [False, "Enable admin message",           "checkbox"],
        "ADMIN_MSG":     ["",    "Admin message",                  "text"],
        "ADMIN_ERRORS":  [False, "Send fatal errors to admin",     "checkbox"],
        "ADMIN_MAIL":    ["",    "Chief admin email address",      "text"],
        "SECRET_KEY":    [None,  "Application secret key",         "text"]
    }

# Logging configuration
logging_format = '[%(levelname)s] %(asctime)s %(message)s'

dictConfig({
    'version': 1,
    'formatters':
    {
        'default':
        {
            'format': logging_format,
            'datefmt': "%Y-%d-%m %H:%M:%S",
        }
    },
    'handlers': {
        'wsgi':
        {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
            'level': 'ERROR'
        },
        'stderr':
        {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
            'level': 'ERROR'
        },
        'file':
        {
            'class': 'logging.FileHandler',
            'filename': LOG_PATH,
            'formatter': 'default',
            'level': 'ERROR'
        }
    },
    'root':
    {
        'level': 'ERROR',
        'handlers': ['wsgi', 'stderr', 'file']
    }

})


# Application itself
app = Flask(__name__)

# Temporary app secret key
# Will be either replaced after configuration
# or loading from database
app.secret_key = token_hex(16)

# Save avatar path to config
app.config["AVATAR_PATH"] = path.abspath(path.join(AVATAR_PATH))
