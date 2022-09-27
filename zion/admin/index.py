from flask import (Blueprint,
                   session,
                   abort,
                   current_app,
                   render_template)


admin_index = Blueprint('admin_index', __name__,
                        url_prefix='/admin',
                        static_folder='static')


@admin_index.route("/dashboard")
@admin_index.route("/")
def index():
    db = current_app.config["DATABASE"]
    if 'username' not in session:
        abort(404)
    return render_template("admin/index.html", USERNAME=session['username'])
