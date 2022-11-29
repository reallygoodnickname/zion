from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   session,
                   flash,
                   url_for,
                   current_app)

import re

from secrets import token_hex

registration = Blueprint('registration', __name__, url_prefix='/')


@registration.before_request
def before_request():
    if 'username' in session:
        return redirect(url_for("index.root_index"))


@registration.route("/registration", methods=["GET", "POST"])
def view():
    if request.method == "GET":
        return render_template("registration.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        rpassword = request.form.get("rpassword")

        if current_app.config["REQUIRE_MAIL"]:
            email = request.form.get("email")

            regex = "^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@" +\
                    "[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$"

            if not re.search(regex, email):
                flash("Wrong email format!")
                return redirect(url_for("registration.view"))

        if password != rpassword:
            flash("Passwords do not match!")
            return redirect(url_for("registration.view"))

        if len(password) < 6:
            flash("Password should be longer than 6 chars!")
            return redirect(url_for("registration.view"))

        _validate = current_app.config["USERS"].validate_username(username)
        if type(_validate) != bool:
            flash(_validate)
            return redirect(url_for("registration.view"))

        if current_app.config["REQUIRE_MAIL"]:
            # Get unvalidate username, pass and mail
            session['uv_username'] = username
            session['uv_password'] = password
            session['uv_email'] = email

            # Gen token
            session['uv_token'] = token_hex(32)

            # Send registration mail with token
            current_app.config["MAILER"].send_registration(session['uv_email'],
                                                           session['uv_token'])

            # Disable permanent session so token can expire
            session.permanent = False

            # Redirect to validate page
            return redirect(url_for("registration.validate"))

        current_app.config["USERS"].add_user(username=username,
                                             password=password,
                                             email="")

        return redirect(url_for("index.root_index"))


@registration.route("/registration/confirm", methods=["GET", "POST"])
def validate():
    # Check if user has uv_token
    if 'uv_token' not in session:
        return redirect(url_for("index.root_index"))

    users_obj = current_app.config["USERS"]
    if request.method == "GET":
        return render_template("confirm.html")
    else:
        # Get token from the user input
        token = request.form.get('token')

        # Check if token stored in session matches received one
        if token != session['uv_token']:
            flash("Codes do not match!")
            return redirect(url_for('registration.validate'))
        else:
            session.pop('uv_token', None)
            users_obj.add_user(username=session['uv_username'],
                               password=session['uv_password'],
                               email=session['uv_email'])
            session.pop('uv_username', None)
            session.pop('uv_password', None)
            session.pop('uv_email', None)

            return redirect(url_for("index.root_index"))
