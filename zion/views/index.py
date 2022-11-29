from flask import (Blueprint,
                   render_template,
                   redirect,
                   flash,
                   url_for,
                   session,
                   request,
                   current_app)

from random import choice

index = Blueprint('index', __name__, url_prefix='/')


@index.route("/")
def root_index():
    if 'username' in session:
        _user = current_app.config["USERS"].get_user(
            username=session['username'])
    else:
        _user = False
    _posts = current_app.config["POSTS"].get_posts()

    if current_app.config["ADMIN_ENABLED"]:
        ADMIN_MSG = current_app.config["ADMIN_MSG"]
    else:
        ADMIN_MSG = None
    return render_template('index.html',
                           ADMIN_MSG=ADMIN_MSG,
                           Posts=_posts,
                           user=_user)


@index.route("/random")
def random():
    # Get post and post post id
    _posts = current_app.config["POSTS"].get_posts()
    _post_id = str(choice(_posts).id)  # nosec

    # Render page with post id
    return redirect(url_for("article.view", post_id=_post_id))


@index.route("/logout")
def logout():
    # Remove all entries from session
    for entry in ['username', 'admin']:
        session.pop(entry, None)

    return redirect(url_for('index.root_index'))


@index.route("/login", methods=['GET', 'POST'])
def login():
    # Leave login page if user already logged in
    if 'username' in session:
        return redirect(url_for('index.root_index'))

    # Get database object from Flask config
    db = current_app.config["USERS"]

    if request.method == 'POST':
        # Get username and password from form
        _username = request.form['username']
        _password = request.form['password']

        valid = current_app.config["USERS"].validate_username(_username)
        if type(valid) != bool:
            flash(valid)
            return render_template("login.html")

        # Check if password has correct length
        if len(_password) < 6:
            flash("Password should be longer than 6 chars!")
            return render_template("login.html")

        # Validate user
        if (db.validate_user(_username, _password)):
            # Get user from database
            user = db.get_user(username=_username)

            # Save user privs in session
            session['username'] = _username
            session['admin'] = user.admin

            # Return back to home
            return redirect(url_for("index.root_index"))
        else:
            # Render template with error message
            flash("Incorrect username or password!")
            return render_template("login.html")
    else:
        # Render login page if request is GET
        return render_template("login.html")
