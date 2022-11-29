import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader
from os import path


class Mailer():
    def __init__(self, user=None, _pass=None,
                 host="localhost", port=465, TLS=False):
        self.__logger = logging.getLogger(__name__)
        if user is not None:
            self.sender = user + "@" + host

        try:
            if TLS:
                self.mailer_obj = smtplib.SMTP_SSL(host=host, port=port)
            else:
                self.mailer_obj = smtplib.SMTP(host=host, port=port)
        except smtplib.SMTPConnectError:
            self.__logger.critical("Failed to connect to mail server")
            exit(1)

        # Trying to login if username and password are required
        if user is not None:
            try:
                self.mailer_obj.login(user, _pass)
            except smtplib.SMTPAuthenticationError:
                self.__logger.critical(
                    "Failed to authenticate to mail server. Check your creds!")
                exit(1)

        # Add jinja templates to http mail
        templates_path = path.join(path.dirname(__file__), "templates", "mail")
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_path), autoescape=True)
        self.jinja_env.list_templates()

    def __del__(self):
        # Stopping mail
        if hasattr(self, "mailer_obj"):
            try:
                self.mailer_obj.quit()
            except smtplib.SMTPServerDisconnected:
                # Actually do nothing, already disconnected
                pass

    # Inner class function to send mail
    def __send_mail(self, from_addr, to_addr, subject, body, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_addr
        message["To"] = to_addr

        body = MIMEText(body, 'plain')
        html = MIMEText(html, 'html')

        message.attach(body)
        message.attach(html)

        try:
            self.mailer_obj.sendmail(from_addr, to_addr, message.as_string())
            return True
        except smtplib.SMTPRecipientsRefused:
            self.__logger.critical(
                "None of the recipients received mail, all refused.")
        except smtplib.SMTPHeloError:
            self.__logger.critical(
                "Server didn't reply to the HELO greeting correctly.")
        except smtplib.SMTPDataError:
            self.__logger.critical(
                "Mail server replied with unexpected error code.")
        except smtplib.SMTPSenderRefused:
            self.__logger.critical(
                "Sender address was refused by mail server.")
        # Will be returned if any errors occur
        return False

    # Send notifications to some user
    def send_registration(self, target_user, code):
        body = f'Your registration code is: {code}. Don\'t tell it to anyone!'

        body_html = self.jinja_env.get_template("registration.html")
        body_html = body_html.render(registration_code=code)

        return self.__send_mail(self.sender, target_user,
                                "Confirm registration", body, body_html)

    def send_error(self, target_user, error):
        body = f'Something went completely wrong, here is traceback:\n{error}'

        body_html = self.jinja_env.get_template("error.html")
        body_html = body_html.render(error=error)

        return self.__send_mail(self.sender, target_user, "Fatal error",
                                body, body_html)
