from flask import (Blueprint,
                   redirect,
                   url_for,
                   session)

logout = Blueprint('logout', __name__, url_prefix='/')


@logout.route("/logout", methods=['GET'])
def root_logout():
    session.pop('username', None)
    return redirect(url_for('index.root_index'))
