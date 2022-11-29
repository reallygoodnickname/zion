from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   session,
                   abort,
                   request,
                   current_app)

from zion.database import Post
from datetime import datetime

import bleach

article = Blueprint('article', __name__, url_prefix='/article')


@article.before_request
def before():
    if 'username' not in session and request.endpoint != "article.view":
        return redirect(url_for("index.root_index"))


@article.route("/view?id=<int:post_id>", methods=["GET"])
@article.route("/view?id=<int:post_id>#<int:comment_id>")
def view(post_id, comment_id=None):

    # Get post and post navigation links
    _post = current_app.config["POSTS"].get_post(post_id=post_id)
    if 'username' in session:
        _user = current_app.config["USERS"].get_user(
            username=session['username'])
    else:
        _user = False

    # Redirect to home if post doesn't exist
    if not _post:
        return redirect(url_for("index.root_index"))

    # Get top-level comments and unfold their children
    _temp = [c for c in _post.comments if c.level < 1]
    _post.comments = _unfold_comments(_temp)

    _posts_nav = current_app.config["POSTS"].get_post_nav(post_id)

    # Render template with navigation links and post
    return render_template("article.html",
                           post_nav=_posts_nav,
                           Post=_post,
                           user=_user,
                           comment_id=comment_id)


@article.route("/view/edit?id=<int:comment_id>", methods=["GET"])
def comment_edit(comment_id):
    comments_obj = current_app.config["COMMENTS"]
    posts_obj = current_app.config["POSTS"]

    _comment = comments_obj.get_comment(comment_id)
    if not _comment:
        abort(404)

    _post = posts_obj.get_post(_comment.post_id)
    if not (_post):
        abort(404)

    _posts_nav = posts_obj.get_post_nav(post_id=_comment.post_id)

    return render_template("article.html",
                           post_nav=_posts_nav,
                           Post=_post,
                           edit=True,
                           comment_id=_comment.id)


@article.route("/view/reply?id=<int:comment_id>", methods=["GET"])
def reply(comment_id):
    comments_obj = current_app.config["COMMENTS"]
    posts_obj = current_app.config["POSTS"]

    # Get comment and post and check if they exist
    _comment = comments_obj.get_comment(comment_id)
    if not (_comment):
        abort(404)

    _post = posts_obj.get_post(post_id=_comment.post_id)
    if not (_post):
        abort(404)

    _posts_nav = posts_obj.get_post_nav(post_id=_comment.post_id)

    return render_template("article.html",
                           post_nav=_posts_nav,
                           Post=_post,
                           reply=True,
                           comment_id=comment_id)


@article.route("/preview", methods=["POST", "GET"])
def preview():
    users_obj = current_app.config["USERS"]

    # Get header and body of the article
    header = request.form.get("header")
    body = request.form.get("body")

    # Check if we have received body and header
    if None in [body, header]:
        return redirect(url_for("index.root_index"))

    # Sanitizing user article, allowing only restricted tags
    body = bleach.clean(body, tags=['b', 'p', 'img', 'a', 'center'],
                        attributes={"*": ["style"], "img": ["src"]})

    # Gettings current timestamp and author's id
    _timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _author = users_obj.get_user(username=session["username"]).id

    # Creating post object
    _post = Post(header=header, article=body,
                 author_id=_author, timestamp=_timestamp)

    # Render article preview if everything is ok
    return render_template('article.html', Post=_post)


@article.route("/delete?id=<int:post_id>")
def delete(post_id):
    posts_obj = current_app.config["POSTS"]

    # Get post by id and delete it if everything is ok
    _post = posts_obj.get_post(post_id=post_id)

    # Check if user either author of the post or moderator
    if _post.author.username == session["username"] or session["moderator"]:
        current_app.config["POSTS"].del_post(_post)

    # Redirect to home page
    return redirect(url_for("index.root_index"))


@article.route("/edit", methods=["GET", "POST"])
@article.route("/edit?id=<int:post_id>", methods=["GET", "POST"])
def edit(post_id=None):
    # Get user and checks it's permissions
    user = current_app.config["USERS"].get_user(username=session['username'])
    if not user:
        return redirect(url_for("index.root_index"))
    else:
        if True not in [user.author, user.admin]:
            abort(403)

    # Get id from request and current timestamp
    _timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if any error received
    _error = request.form.get("error")
    if _error is not None:
        return render_template("editor.html", error_msg=_error,
                               timestamp=_timestamp, Post=False)

    # Render empty editor of no ID is specified
    if post_id is None:
        return render_template("editor.html", timestamp=_timestamp, Post=False)

    _post = current_app.config["POSTS"].get_post(post_id)

    # Return 403 if user is not admin and not author of the text
    if _post.author.username != session["username"] and not session["admin"]:
        abort(403)

    return render_template("editor.html", Post=_post)


@article.route("/update?id=<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    # Get post and check if it exists
    _post = current_app.config["POSTS"].get_post(post_id)
    if not _post:
        abort(404)

    # Return 403 if user is not admin and not author of the text
    if _post.author.username != session["username"] and not session["admin"]:
        abort(403)

    # Get all necessary information from form
    _post.header = request.form.get("header")
    _post.article = request.form.get("body")

    # Validate input and render error if validation fail
    _validate = _validate_input(_post.header, _post.article)

    if _validate is not True:
        return redirect(url_for("index.root_index"))

    # Update post information
    current_app.config["POSTS"].update_post(_post)

    # Redirect to home page
    return redirect(url_for("index.root_index"))


@article.route("/add", methods=["GET", "POST"])
def add():
    users_obj = current_app.config["USERS"]

    # Get required information from form and session
    _header = request.form.get("header")
    _article = request.form.get("body")
    _author = users_obj.get_user(username=session["username"]).id

    # Validate input and render error if validation fail
    _validate = _validate_input(_header, _article)
    if _validate is not True:
        return _validate

    # And post with specified info
    current_app.config["POSTS"].add_post(_header, _article, _author)

    # Return back to home page
    return redirect(url_for("index.root_index"))


# Check article header and post sizes
def _validate_input(header, article):
    # Validate header and article length
    if ((len(header) < 40 or len(header) > 120) or
            (len(article) < 1000 or len(article) > 10000)):
        return redirect(url_for("index.root_index"))

    # Return true is everthing is ok
    return True


# Function to get all children and parents in one list with the same order
def _unfold_comments(_comments):
    _list = []

    for comment in _comments:
        _list.append(comment)
        for sub in _unfold_comments(comment.child):
            _list.append(sub)

    return _list
