from flask_mail import Message
from flask import url_for
from flaskapp import mail


def send_reset_email(user):
    if user:
        token = user.get_reset_token()
        message = Message('Reset Hasła', recipients=[user.email])
        message.body = f'''Aby przypisać do swojego konta nowe hasło kliknij w poniższy link: 
{url_for('users.reset_password_token', token=token, _external=True)}


Ważność linku to 30 minut!
Zignoruj link, jeżeli to nie ty wywołałeś zmainę hasła.
'''
        mail.send(message)
