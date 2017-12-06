#-*- coding: utf8 -*-
from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread
import os, config

#Send email asynchronous
def send_async_mail(app, msg, mail):
    with app.app_context():
        mail.send(msg)


def send_mail(to, user, token):
    app = current_app._get_current_object()
    app.config.from_object(config)
    mail = Mail(app)
    msg = Message('Confirm Your Account', sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = render_template('confirm.txt', user=user, token=token)

    thr = Thread(target=send_async_mail, args=[app, msg, mail])
    thr.start()
    return '<h1>OK!</h1>'

