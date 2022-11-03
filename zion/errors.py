from flask import (Blueprint,
                   render_template)

errors = Blueprint('error', __name__,
                   template_folder='templates',
                   static_folder='static',
                   url_prefix='/')


@errors.app_errorhandler(Exception)
def error_handler(error):
    if error.code in [403, 404]:
        return render_template(f"{error.code}.html")
    else:
        # Render page with excuses and send email notification
        # to someone responsible for this mess

        # TODO: add email notification
        return render_template("50x.html")
