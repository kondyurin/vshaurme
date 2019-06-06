from threading import Thread

from flask import current_app, render_template
from flask_mail import Message
from flask_babel import lazy_gettext as _l

from vshaurme.extensions import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()


def send_confirm_email(user, token, to=None):
    send_mail(subject=_l('Email Confirm'), to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject=_l('Password Reset'), to=user.email, template='emails/reset_password', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject=_l('Change Email Confirm'), to=to or user.email, template='emails/change_email', user=user, token=token)
