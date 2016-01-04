

import sys

from passlib.hash import pbkdf2_sha512
import base64
import hashlib
import hmac

from sqlalchemy import create_engine

from config import DATABASE_URI, SALT

def get_hmac(pw):
    # from flask-security source 
    # https://github.com/mattupstate/flask-security/blob/develop/flask_security/utils.py#L96
    h = hmac.new(SALT, pw, hashlib.sha512)
    return base64.b64encode(h.digest())

def encrypt_password(pw):
    # also from flask-security source
    # https://github.com/mattupstate/flask-security/blob/develop/flask_security/utils.py#L143
    signed = get_hmac(pw).decode('ascii')
    return pbkdf2_sha512.encrypt(signed)

# TODO do this through an admin panel on the web frontend
if __name__ == '__main__':
    email = sys.argv[1]
    pw = sys.argv[2]
    engine = create_engine(DATABASE_URI)
    enc_pw = encrypt_password(pw)
    engine.execute(
            "INSERT INTO user (email, password, active) VALUES (?, ?, ?)",
            email,
            enc_pw,
            1)

