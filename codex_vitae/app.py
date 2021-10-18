# Python standard libraries
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin,
    )
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from gcp_utils import init_connection_engine
from etl.orm_inserts import etl_init
from data_viz import journal_calendar


# Configuration
GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
GOOGLE_CLIENT_SECRET =  os.getenv("CLIENT_SECRET")

GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'
DB_URL = os.getenv("DB_URL")
EMAIL = os.getenv("EMAIL")

# TODO: Resolve testing with this initial database declaration.
db = None

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# User class for flask-login
class User(UserMixin):
    def __init__(self, email):
        self.id = email

    @staticmethod
    def get(user_id):
        user = User(email=user_id)
        return user

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# TODO: Add error handling
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/")
def login():
    # Find out what URL to hit for Google login.
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construct Google login request and retrieve user profile.
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "login/callback",
        scope=["openid", "email", "profile"],
        )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code from Google.
    code = request.args.get("code")

    # Get User token URL.
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens.
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
        )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )

    # Parse tokens.
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get Google account information,
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Verify email address for Google account.
    if userinfo_response.json()["email"] != EMAIL:
        return "User email not available or not verified by Google.", 400

    user = User(email=EMAIL)

    # Begin user session by logging the user in
    login_user(user)

    # Send user to homepage if Google account is verified.
    return redirect(url_for("codex_vitae"))


@login_required
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for("login"))


@login_required
@app.route('/codex-vitae')
def codex_vitae():
    if current_user.is_authenticated:
        # Connect to DB and plot journal entries.
        global db
        db = db or init_connection_engine()

        with db.connect() as conn:
            journal_tuples = conn.execute(
                                        "select * from journal_prod order by date"
                                        ).fetchall()

        journal = journal_calendar(journal_tuples)

        return render_template('index.html', plot=journal)
    return "Please Log In."


if __name__ == '__main__':

    app.run(ssl_context="adhoc",debug=True)
