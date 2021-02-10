from demabets.email_factory import email_blueprint
from flask import render_template, Blueprint, copy_current_request_context
from flask_mail import Message
from demabets import mail


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Demabets] Reset Your Password',
               sender='accounts@demabets.com',
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_confirmation_email(user):
    token = user.get_confirmation_token()
    send_email('[Demabets] Activate your account',
               sender='accounts@demabets.com',
               recipients=[user.email],
               text_body=render_template('email/activate_account.txt',
                                         user=user, token=token),
               html_body=render_template('email/activate_account.html',
                                         user=user, token=token))