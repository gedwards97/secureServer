# Session object requires the application to have a vlaue set for SECRET_KEY variable
# SECRET_KEY used to encrypt session cookie -> complex SECRET_KEY suggested

import secrets
from flask import session
secret_key = secrets.token_urlsafe(20)
print(secret_key)

session["USERNAME"] = "George"
print(session["USERNAME"])