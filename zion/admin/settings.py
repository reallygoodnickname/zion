from flask import (Blueprint,
                   session,
                   render_template,
                   abort)

admin_settings = Blueprint('admin_settings', __name__,
                           url_prefix='/admin',
                           static_folder='static')


@admin_settings.route('/settings')
def settings():
    # Returning 404 if not logged in
    # to protect admin page
    if 'username' not in session:
        abort(404)

    return render_template("admin/settings.html", USERNAME=session['username'])
