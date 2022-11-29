from flask import (Blueprint,
                   render_template,
                   flash,
                   redirect,
                   session,
                   request,
                   url_for,
                   abort,
                   current_app)

from secrets import token_urlsafe
from zion.database import User

import os

profile = Blueprint('profile', __name__, url_prefix='/')

ALLOWED_EXTENSIONS = [".jpeg", ".jpg", ".png"]


@profile.route("/profile?name=<username>")
def view(username):
    # Get profile and check if it exists
    _profile = current_app.config["USERS"].get_user(username=username)
    if not _profile:
        abort(404)

    return render_template('profile.html', profile=_profile)


@profile.route("/profile/update", methods=["POST"])
def update():

    users_obj = current_app.config["USERS"]
    _user = users_obj.get_user(username=session['username'])

    _username = request.form.get("username")

    _old_password = request.form.get("old-password")
    _new_password = request.form.get("new-password")

    _avatar = request.files["avatar"]

    if len(_username) < 6 or len(_username) > 20:
        flash("Username length should be from 6 to 20 chars!")
        return redirect(url_for("profile.view",
                                username=session['username']))

    # Check if username does not contain bad chars
    elif not _username.isalnum():
        flash("Username can contain only aphanum. characters")
        return redirect(url_for("profile.view",
                                username=session['username']))

    # Process image change
    if len(_avatar.filename) != 0:
        # Get file extension
        _extension = "."+_avatar.filename.split(".")[-1].lower()

        # Check if uploaded file's extension is allowed
        if _extension not in ALLOWED_EXTENSIONS:
            flash("Wrong file extension!")
            return redirect(url_for("profile.view",
                                    username=session['username']))

        # Generate new filename
        _avatar.filename = token_urlsafe(10) + _extension

        # Generate new filename is current one exists in table
        while users_obj._exists_in_table(User.avatar, _avatar.filename):
            _avatar.filename = token_urlsafe(10)+_extension
    else:
        _avatar.filename = None

    if _avatar.filename is not None:
        # Get image base path
        base_path = current_app.config["AVATAR_PATH"]

        # Set new avatar
        _avatar.save(os.path.join(base_path, _avatar.filename))

        # Delete previous one
        if _user.avatar is not None:
            os.remove(os.path.join(base_path, _user.avatar))

    # Update profile and set new username
    users_obj.update_profile(_user.id, _username, _avatar.filename)
    session['username'] = _username

    # Process password change
    if '' not in [_old_password, _new_password]:
        if not len(_new_password) > 6:
            flash("New password should be longer than 6 chars!")
        else:
            if users_obj.validate_user(session['username'], _old_password):
                users_obj.change_password(_user, _new_password)
                for entry in ['username', 'admin', 'author', 'moderator']:
                    session.pop(entry, None)
            else:
                flash("Old password is wrong!")

    # Redirect to home if logged out after password change
    if 'username' not in session:
        return redirect(url_for("index.root_index"))

    return redirect(url_for("profile.view", username=session['username']))


@profile.route('/profile/delete', methods=["GET"])
def delete():
    user = current_app.config["USERS"].get_user(username=session['username'])

    # Check if user exists in db
    if not user:
        return redirect(url_for("index.root_index"))

    # Remove everything from session
    for entry in ['username', 'admin']:
        session.pop(entry, None)

    # Completely delete user
    current_app.config["USERS"].del_user(user)

    # Redirect to index
    return redirect(url_for("index.root_index"))
