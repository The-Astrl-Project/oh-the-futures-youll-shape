#
# Copyright (c) 2024 Astrl.
#
# This file is part of oh-the-futures-youll-shape. It is subject to the license terms in
# the LICENSE file found in the top-level directory of this project and at
# https://github.com/The-Astrl-Project/oh-the-futures-youll-shape/blob/HEAD/LICENSE.
#
# This file may not be copied, modified, propagated, or distributed
# except according to the terms contained in the LICENSE file.
#

# Import Statements
# ----------------------------------------------------------------
from os import environ
from typing import Final
# ---
from bot.bot import SearchQuery, search
# ---
import flask
from flask_socketio import SocketIO
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || app.py
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants
__version__: Final[str] = "0.1.0-DEV"

# Public Variables

# Private Variables
app: Final[flask.Flask] = flask.Flask(__name__, template_folder="templates")
socket: SocketIO = SocketIO(app=app)

# Routes
@app.get("/")
def route_home() -> None:
    # Populate the current session
    if "state" not in flask.session:
        # Create a new state
        flask.session["state"] = None

    if "credentials" not in flask.session:
        # Create a new credentials
        flask.session["credentials"] = None

    # Render the home page
    return flask.render_template("home.html")

@app.get("/callback")
def route_callback() -> None:
    # Retrieve the OAuth state
    oauth_state = flask.session.get("state")

    # Create a new OAuth flow
    oauth_control_flow: Flow = Flow.from_client_secrets_file(
        "keys.json",
        state=oauth_state,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    oauth_control_flow.redirect_uri = flask.url_for("route_callback", _external=True)

    # Get the callback response
    oauth_response = flask.request.url
    oauth_control_flow.fetch_token(authorization_response=oauth_response)

    # Store the credentials in the session
    oauth_credentials = oauth_control_flow.credentials
    flask.session["credentials"] = {
        "token": oauth_credentials.token,
        "refresh_token": oauth_credentials.refresh_token,
        "token_uri": oauth_credentials.token_uri,
        "client_id": oauth_credentials.client_id,
        "client_secret": oauth_credentials.client_secret,
        "scopes": oauth_credentials.scopes,
    }

    # Redirect
    return flask.redirect(flask.url_for("route_home"))

# Transport Socket
@socket.on("client_message")
def handle_message(message) -> None:
    # Parse as dict
    message_data: Final[dict] = message

    # Check the message type
    if message_data.get("type") == "request":
        # Check the request type
        if message_data.get("data_type") == "user_profile":
            # Check for credentials
            if flask.session.get("credentials") == None:
                # No credentials found
                return socket.emit(
                    "server_message",
                    {
                        "type": "response",
                        "response_type": "user_profile",
                        "data": None,
                        "transport_client_id": message_data.get("transport_client_id"),
                    },
                )

            # Load the credentials stored in the session
            credentials = Credentials(**flask.session.get("credentials"))

            # Build the People API service
            people_api_service = build("people", "v1", credentials=credentials)
            results = (
                people_api_service.people()
                .get(resourceName="people/me", personFields="photos")
                .execute()
            )

            # Return the user profile
            return socket.emit(
                "server_message",
                {
                    "type": "response",
                    "response_type": "user_profile",
                    "data": results.get("photos")[0].get("url"),
                    "transport_client_id": message_data.get("transport_client_id"),
                },
            )

        if message_data.get("data_type") == "search":
            # Check for credentials
            if flask.session.get("credentials") == None:
                # No credentials found
                return socket.emit(
                    "server_message",
                    {
                        "type": "response",
                        "response_type": "search",
                        "data": None,
                        "transport_client_id": message_data.get("transport_client_id"),
                    },
                )

            # TODO: Finish this method
            print(message_data.get("args"))

    # Check the message type
    if message_data.get("type") == "oauth":
        # Check the oauth type
        if message_data.get("data_type") == "register":
            # Generate a OAuth control flow
            oauth_control_flow: Flow = Flow.from_client_secrets_file(
                "keys.json",
                scopes=[
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/spreadsheets",
                ],
            )

            # Configure the redirect URI
            oauth_control_flow.redirect_uri = "http://127.0.0.1:5000/callback"

            # Generate the OAuth URL and the OAuth state
            oauth_url, oauth_state = oauth_control_flow.authorization_url(
                access_type="offline", include_granted_scopes="true", prompt="consent"
            )

            # Store the state in the current session
            flask.session["state"] = oauth_state

            # Prompt OAuth redirection
            return socket.emit(
                "server_message",
                {
                    "type": "oauth",
                    "response_type": "register",
                    "data": oauth_url,
                    "transport_client_id": message_data.get("transport_client_id"),
                },
            )

# Private Methods

# Script Check
if __name__ == "__main__":
    # Print project info
    print(f"Oh, the Futures You'll Shape || Web Server v{__version__}\nCopyright (c) 2024 Astrl\n\n")

    # Configure the environment
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Configure the app
    app.config["SECRET_KEY"] = "ASTRL_DEV"

    # Run as development
    socket.run(app, host="0.0.0.0", port="5000", debug=True)
