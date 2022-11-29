from flask import (Blueprint,
                   render_template,
                   abort,
                   request,
                   redirect,
                   flash,
                   url_for,
                   current_app)

from secrets import token_hex

config = Blueprint('config', __name__, url_prefix='/')


@config.route("/config", methods=["GET", "POST"])
def configure():
    if request.method == "GET":
        # Render config template if application is not configured
        return render_template("config.html",
                               _configured=current_app.config["CONFIGURED"])
    else:
        if current_app.config["CONFIGURED"]:
            abort(403)

        _username = request.form.get("username")
        _password = request.form.get("password")
        _pwrepeat = request.form.get("password-repeat")
        _email = request.form.get("email")

        if len(_email) < 1:
            _email = None

        # Some input validations
        if _pwrepeat != _password:
            flash("Passwords do not match!")
            return redirect(url_for("config.configure"))

        _validate = current_app.config["USERS"].validate_username(_username)
        if type(_validate) != bool:
            flash(_validate)
            return redirect(url_for("config.configure"))

        if not 6 < len(_password):
            flash("Password size should be from 6 to 20 chars!")
            return redirect(url_for("config.configure"))

        if current_app.config["USERS"].get_user(username=_username):
            flash("Username already taken!")
            return redirect(url_for("config.configure"))

        if _email is not None:
            if not current_app.config["USERS"].validate_mail(_email):
                flash("Email format wrong")
                return redirect(url_for("config.configure"))
        else:
            _email = ""

        current_app.config["USERS"].add_user(username=_username,
                                             password=_password,
                                             email=_email,
                                             admin=True)

        # Set admin email
        current_app.config["SETTINGS"].change_setting("ADMIN_MAIL", _email)

        # Set new secret key and save it to db
        current_app.secret_key = token_hex(32)
        current_app.config["SECRET_KEY"] = current_app.secret_key
        current_app.config["SETTINGS"].change_setting("SECRET_KEY",
                                                      current_app.secret_key)

        # Change application state to configured
        current_app.config["CONFIGURED"] = True

        # TODO: add email validation
        return redirect(url_for("index.root_index"))
