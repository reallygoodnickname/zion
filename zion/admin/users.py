from flask import (Blueprint,
                   flash,
                   session,
                   current_app,
                   redirect,
                   abort,
                   request,
                   url_for,
                   render_template)

admin_users = Blueprint('admin_users', __name__,
                        url_prefix='/admin',
                        static_folder='static')


@admin_users.before_request
def check_permissions():
    if 'username' in session:
        if not session['admin']:
            abort(403)
    else:
        abort(403)


@admin_users.route('/users')
def users():
    Users = current_app.config["USERS"].get_users()
    return render_template("admin/users.html", Users=Users)


@admin_users.route('/users/delete?id=<int:user_id>', methods=['GET'])
def delete(user_id):
    users_obj = current_app.config["USERS"]

    # Getting user by id and deleting it from
    _user = users_obj.get_user(user_id=user_id)

    # Abort if username not found
    if not _user:
        flash("User not found!")
    else:
        users_obj.del_user(_user)

        # Ending session if user logged in
        if _user.username == session['username']:
            for entry in ['username', 'admin']:
                session.pop(entry, None)
            return redirect(url_for("index.root_index"))

    return redirect(url_for("admin_users.users"))


@admin_users.route("/users/alter?id=<int:user_id>&field=<field>")
def alter(user_id, field):
    users_obj = current_app.config["USERS"]

    _user = users_obj.get_user(user_id)
    if not _user:
        flash("User not found!")
    else:
        users_obj.swap_permission(_user, field)

    return redirect(url_for("admin_users.users"))


@admin_users.route("/users/add", methods=["GET", "POST"])
def add():
    users_obj = current_app.config["USERS"]
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rpassword = request.form.get("rpassword")
        email = request.form.get("email")

        validate = users_obj.validate_username(username)
        if type(validate) != bool:
            flash(validate)
            return redirect(url_for("admin_users.add"))

        # Convert None to empty string and validate mail format
        if email != "":
            if not users_obj.validate_mail(email):
                flash("Incorrect mail format!")
                return redirect(url_for("admin_users.add"))

        if password != rpassword:
            flash("Passwords do not match!")
        elif len(password) < 6:
            flash("Password should be longer than 6 chars!")
            return redirect(url_for("admin_users.add"))

        if not users_obj.add_user(username, password, email):
            flash("Failed to add user! :(")
            return redirect(url_for("admin_users.users"))

        return redirect(url_for("admin_users.users"))
    else:
        return render_template("admin/new_user.html")


@admin_users.route("/users/edit?username=<username>", methods=["GET", "POST"])
def edit(username):
    users_obj = current_app.config["USERS"]
    if request.method == "POST":
        user = users_obj.get_user(username=username)
        username = request.form.get("username")
        email = request.form.get("email")

        validate = users_obj.validate_username(username)
        if type(validate) != bool:
            flash(validate)
            return redirect(url_for("admin_users.edit", username=username))

        # Convert None to empty string and validate mail format
        if email != "":
            if not users_obj.validate_mail(email):
                flash("Incorrect mail format!")
                return redirect(url_for("admin_users.edit", username=username))

        users_obj.update_profile(_id=user.id, username=username, email=email)

        return redirect(url_for("admin_users.users"))
    else:
        user = users_obj.get_user(username=username)
        if not user:
            flash("User not found!")
            return redirect(url_for("admin_users.users"))
        return render_template("admin/new_user.html", user=user)
