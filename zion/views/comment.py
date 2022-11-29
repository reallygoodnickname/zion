from flask import (Blueprint,
                   redirect,
                   url_for,
                   session,
                   abort,
                   request,
                   current_app)

comment = Blueprint('comment', __name__, url_prefix='/article/comment')


@comment.before_request
def _logged_in():
    if 'username' not in session:
        return redirect(url_for("index.root_index"))


@comment.route("/add?id=<int:post_id>", methods=["POST", "GET"])
@comment.route("/add?id=<int:post_id>&reply=<int:parent_id>", methods=["POST", "GET"])
def add(post_id, parent_id=None):
    comments_obj = current_app.config["COMMENTS"]

    if parent_id is not None:
        _parent_comment = comments_obj.get_comment(parent_id)
        if not _parent_comment:
            abort(404)

    _content = request.form.get("comment")

    # Get author id
    _author = current_app.config["USERS"].get_user(
        username=session['username']).id

    # Get level, set 0 if not a reply
    _level = 0 if parent_id is None else _parent_comment.level+1

    # Add comment
    comments_obj.add_comment(post_id=post_id,
                             author=_author,
                             parent_id=parent_id,
                             level=_level,
                             content=_content)

    return redirect(url_for("article.view", post_id=post_id))


@comment.route("/delete?id=<int:comment_id>", methods=["POST", "GET"])
def delete(comment_id):
    comments_obj = current_app.config["COMMENTS"]

    _comment = comments_obj.get_comment(comment_id)
    if not _comment:
        abort(404)

    _author = _comment.author.username

    if ((_author == session["username"]) or
            session["moderator"] or
            session["admin"]):
        comments_obj.del_comment(_comment)

    return redirect(url_for("article.view", post_id=_comment.post_id))


@comment.route("/edit?id=<int:comment_id>", methods=["POST", "GET"])
def edit(comment_id):
    comments_obj = current_app.config["COMMENTS"]

    _comment = comments_obj.get_comment(comment_id)
    if not _comment:
        abort(404)

    _content = request.form.get("comment")
    _post_id = _comment.post_id

    comments_obj.change_comment(_comment.id, _content)

    return redirect(url_for("article.view", post_id=_post_id))
