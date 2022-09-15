from flask import Flask

app = Flask(__name__)
app.secret_key = b'development'

__version__ = '0.0.1'
