from threading import Thread

from flask import current_app, render_template
from flask_mail import Message
from flask_babel import lazy_gettext as _l

from vshaurme.extensions import mail


# def _send_async_mail(app, message):
#     with app.app_context():
#         mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    mail.send(message)
    # thr = Thread(target=_send_async_mail, args=[app, message])
    # thr.start()
    # return thr


def send_confirm_email(user, token, to=None):
    send_mail(subject=_l('Email Confirm'), to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject=_l('Password Reset'), to=user.email, template='emails/reset_password', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject=_l('Change Email Confirm'), to=to or user.email, template='emails/change_email', user=user, token=token)
