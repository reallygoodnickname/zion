from flask import (Blueprint,
                   session,
                   abort,
                   render_template)

admin_security = Blueprint('admin_security', __name__,
                           url_prefix='/admin',
                           static_folder='static')


@admin_security.route('/security')
def security():
    # Returning 404 if not logged in
    # to protect admin page
    if 'username' not in session:
        abort(404)

    return render_template("admin/security.html", USERNAME=session['username'])
