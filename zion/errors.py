from flask import (Blueprint,
                   current_app,
                   render_template)

import traceback

errors = Blueprint('error', __name__,
                   template_folder='templates/errors',
                   static_folder='static',
                   url_prefix='/')


@errors.app_errorhandler(Exception)
def error_handler(error):
    app = current_app

    if not hasattr(error, "code"):

        # Log error
        current_app.logger.error(error)

        # Send mail with error information to admin
        if "MAILER" in app.config and app.config["ADMIN_ERRORS"]:
            err = traceback.TracebackException.from_exception(error).format()
            app.config["MAILER"].send_error(
                current_app.config["ADMIN_MAIL"], "".join(err))

        return render_template("50x.html"), 500

    # Check if error is 403, 404
    if error.code in [403, 404]:
        return render_template(f"{error.code}.html"), error.code
