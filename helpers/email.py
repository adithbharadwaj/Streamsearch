import os
from datetime import datetime, timedelta, timezone
import textwrap
from flask import render_template

import jwt
from flask_mail import Message

SECRET_KEY = os.environ['STREAMSEARCH_SECRET_KEY']
SIGNING_ALGORITHM = 'HS256'
DEFAULT_LIFETIME = 10

def create_token(user_id, lifetime):
    encode_dict = {
        'user_id': user_id,
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=lifetime)
    }
    token = jwt.encode(
        encode_dict,
        SECRET_KEY,
        algorithm=SIGNING_ALGORITHM
    )
    return token

def decode_token(token):
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[SIGNING_ALGORITHM]
    )['user_id']

def send_password_reset_email(mailer, user, lifetime=DEFAULT_LIFETIME):
    token = user.create_jwt(lifetime)

    msg = Message(
        subject='Password reset',
        recipients=[f'{user.email}'],
        sender='noreply@streamsearch.com'
    )
    msg.html = render_template('password-reset-email.html', token=token, lifetime=lifetime)

    with open(os.path.join('static', 'logo', 'main.png'), 'rb') as f:
        msg.attach(
            'streamsearch-logo.png','image/png',
            f.read(),
            'inline',
            headers=[['Content-ID', 'streamsearch-logo'],]
        )

    mailer.send(msg)

def send_account_activation_email(mailer, user, lifetime=DEFAULT_LIFETIME):
    token = user.create_jwt(lifetime)

    msg = Message(
        subject='Account activation',
        recipients=[f'{user.email}'],
        sender='noreply@streamsearch.com'
    )
    msg.html = render_template('signup-confirmation-email.html', token=token, lifetime=lifetime)

    with open(os.path.join('static', 'logo', 'main.png'), 'rb') as f:
        msg.attach(
            'streamsearch-logo.png','image/png',
            f.read(),
            'inline',
            headers=[['Content-ID', 'streamsearch-logo'],]
        )

    mailer.send(msg)
