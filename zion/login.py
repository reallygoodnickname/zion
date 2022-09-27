from flask import (Blueprint,
                   session,
                   abort,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   current_app)

login = Blueprint('login', __name__, url_prefix='/')


@login.route("/login", methods=['GET', 'POST'])
def root_login():
    if 'username' in session:
        return redirect(url_for('index.root_index'))

    db = current_app.config["DATABASE"]

    if request.method == 'POST':
        # TODO: add username badchars check
        if (db.validateUser(request.form['username'],
                            request.form['password'])):
            session['username'] = request.form['username']
            return redirect(url_for('index.root_index'))
        else:
            return render_template('login.html', INVALID_CRED=True)
    else:
        return render_template('login.html')
