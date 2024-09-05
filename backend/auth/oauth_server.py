# OAuth 2.0 flow implementation
# backend/auth/oauth_server.py

from flask import Blueprint, request, redirect, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
from backend.models.user_model import User
from backend import db

oauth_bp = Blueprint('oauth', __name__)

# OAuth configuration (as before)
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@oauth_bp.route('/login')
def login():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri="http://localhost:5000/oauth2callback"
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@oauth_bp.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        state=state,
        redirect_uri="http://localhost:5000/oauth2callback"
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Store tokens in the database
    user = User(
        email="bitarafshh@gmail.com",  # You'd get this from the authenticated session
        access_token=credentials.token,
        refresh_token=credentials.refresh_token
    )
    db.session.add(user)
    db.session.commit()

    return 'Authentication successful! You can close this window.'