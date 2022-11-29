from . import app as app
from .errors import errors

from sqlalchemy.orm import Session, close_all_sessions

from .admin.posts import admin_posts
from .admin.users import admin_users
from .admin.settings import admin_settings

from .views.index import index
from .views.comment import comment
from .views.article import article
from .views.profile import profile
from .views.registration import registration

# Register all brueprints
app.register_blueprint(admin_posts)
app.register_blueprint(admin_users)
app.register_blueprint(admin_settings)

app.register_blueprint(index)
app.register_blueprint(errors)
app.register_blueprint(profile)
app.register_blueprint(article)
app.register_blueprint(registration)
app.register_blueprint(comment)


@app.before_request
def before_request():
    # Create new session for every new request
    app.config["DATABASE"].session = Session(app.config["DATABASE"].engine)


@app.after_request
def after_request(response):
    # Content security policy
    _csp = "default-src 'self';" + \
        "script-src 'none';" + \
        "style-src 'unsafe-inline' 'self' fonts.googleapis.com;" + \
        "img-src *;" + \
        "font-src fonts.gstatic.com;"

    # Set some security headers
    response.headers["X-Frame-Options"] = "deny"
    response.headers["Content-Security-Policy"] = _csp

    return response


@app.teardown_request
def teardown_request(exception):
    # Close all sessions after request is finished
    close_all_sessions()
