from flask import (Blueprint,
                   flash,
                   url_for,
                   session,
                   abort,
                   current_app,
                   redirect,
                   render_template)

admin_posts = Blueprint('admin_posts', __name__,
                        url_prefix='/admin',
                        static_folder='static')


@admin_posts.before_request
def check_permissions():
    if 'username' in session:
        if not session['admin']:
            abort(403)
    else:
        abort(403)


@admin_posts.route('/posts')
def posts():
    Posts = current_app.config["POSTS"].get_posts()
    return render_template("admin/posts.html", Posts=Posts)


@admin_posts.route('/posts/delete?id=<int:post_id>', methods=['GET'])
def delete(post_id):
    # Trying to get arguments from request
    _post = current_app.config["POSTS"].get_post(post_id=post_id)
    if not _post:
        flash("Post not found!")
    else:
        current_app.config["POSTS"].del_post(_post)

    return redirect(url_for("admin_posts.posts"))
