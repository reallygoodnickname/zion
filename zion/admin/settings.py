from flask import (Blueprint,
                   session,
                   current_app,
                   flash,
                   redirect,
                   request,
                   url_for,
                   render_template,
                   abort)

from zion.mailer import Mailer

from smtplib import SMTPAuthenticationError

admin_settings = Blueprint('admin_settings', __name__,
                           url_prefix='/admin',
                           static_folder='static')


@admin_settings.before_request
def check_permissions():
    if 'username' in session:
        if not session['admin']:
            abort(403)
    else:
        abort(403)


@admin_settings.route('/settings/update', methods=["POST"])
def confirm():
    app = current_app
    # Get current application settings
    settings = app.config["ZION_SETTINGS"].copy()
    settings.pop("SECRET_KEY")

    for setting in settings:
        setting_type = settings[setting][2]
        value = request.form.get(setting)

        if setting in ['ADMIN_MAIL'] and settings['ADMIN_MAIL'][0] != "":
            if not app.config['USERS'].validate_mail(value):
                flash("Wrong email adress format!")
                return redirect(url_for("admin_settings.settings"))

        if value in ['on', None] and setting_type == "checkbox":
            value = True if value == 'on' else False

        settings[setting][0] = value

    # Mail validation
    if True in [settings['SMTP_ENABLED'][0], settings['REQUIRE_MAIL'][0],
                settings['ADMIN_ERRORS'][0]]:
        if "" in [settings['SMTP_HOSTNAME'][0], settings['SMTP_USERNAME'][0],
                  settings['SMTP_PASSWORD'][0]]:
            flash("Missing SMTP hostname/username/password")
            return redirect(url_for("admin_settings.settings"))

    # Check if SMTP is enabled to require mail
    if settings['REQUIRE_MAIL'][0] and not settings['SMTP_ENABLED'][0]:
        flash("Can't require mail when SMTP disabled!")
        return redirect(url_for("admin_settings.settings"))

    # Check if SMTP is enabled to require mail
    if settings['ADMIN_ERRORS'][0] and not settings['SMTP_ENABLED'][0]:
        flash("Can't require mail when SMTP disabled!")
        return redirect(url_for("admin_settings.settings"))

    # Try to create mailer object
    if settings['SMTP_ENABLED'][0] and "MAILER" not in app.config:
        try:
            if ":" not in settings['SMTP_HOSTNAME']:
                app.config["MAILER"] = Mailer(settings["SMTP_USERNAME"][0],
                                              settings["SMTP_PASSWORD"][0],
                                              settings["SMTP_HOSTNAME"][0],
                                              port="465", TLS=True)
            else:
                host, port = settings['SMTP_HOSTNAME'].split(":")
                app.config["MAILER"] = Mailer(settings["SMTP_USERNAME"][0],
                                              settings["SMTP_PASSWORD"][0],
                                              host, port, TLS=True)
        except SMTPAuthenticationError:
            flash("Failed to connect to SMTP server, check your creds!")
            return redirect(url_for("admin_settings.settings"))

    # Removing mailer and closing connection if disabled smtp
    if not settings["SMTP_ENABLED"][0] and "MAILER" in app.config:
        del app.config["MAILER"]

    if settings["ADMIN_ENABLED"][0] and len(settings["ADMIN_MSG"][0]) < 5:
        flash("Admin message length should be >5 if enabled!")
        return redirect(url_for("admin_settings.settings"))

        # Write all settings to config file and database
    for setting in settings:
        app.config[setting] = settings[setting][0]
        app.config["SETTINGS"].change_setting(setting, settings[setting][0])

    return redirect(url_for("admin_settings.settings"))


@admin_settings.route('/settings')
def settings():
    # Get current settings
    settings = current_app.config["ZION_SETTINGS"].copy()

    # Remove secret key since it cannot be change by hand
    settings.pop("SECRET_KEY")

    return render_template("admin/settings.html", settings=settings)
