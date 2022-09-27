from flask import (Blueprint,
                   render_template,
                   current_app)

index = Blueprint('index', __name__, url_prefix='/')


@index.route("/")
def root_index():
    ADMIN_MSG = current_app.config["ADMIN_MSG"]
    return render_template('index.html', ADMIN_MSG=ADMIN_MSG)
