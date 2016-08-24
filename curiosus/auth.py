from functools import wraps

from flask import g, redirect, request, session, url_for

from curiosus import bcrypt
from curiosus.models import User


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    if bcrypt.check_password_hash(user.password, password):
        return user

    else:
        return


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login', next=request.url))
        elif isinstance(session.get('user'), User):
            return f(*args, **kwargs)
    return decorated_function
