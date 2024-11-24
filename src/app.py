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

# ---
import quart
from asyncio import CancelledError
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || app.py
#
# A minimal and asynchronous webserver.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Class Definitions
class Server:
    # Enums

    # Interfaces

    # Constants
    __version__: Final[str] = "0.2.0-DEV"

    # Public Variables

    # Private Variables
    _server_config: dict = None
    _app: quart.Quart = None

    # Constructor
    def __init__(self, config: dict) -> None:
        # Store the server configuration
        self._server_config = config

        # Instance a new Quart app
        self._app = quart.Quart(__name__)

        # Configure the Quart app
        self._app.config.update(config)

        # Configure the server routes
        self._app.route("/", methods=["GET"])(self._handle_route_home)
        self._app.route("/callback", methods=["GET"])(self._handle_route_callback)
        self._app.websocket("/transport")(self._handle_route_websocket)

    # Public Static Methods

    # Public Inherited Methods
    def run_app_as_debug(self) -> None:
        # Configure the environment
        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Start the web server
        self._app.run(host="0.0.0.0", port="5000", debug=True, use_reloader=False)

    # Private Static Methods

    # Private Inherited Methods
    async def _handle_route_home(self) -> str:
        # Populate the current session
        if "state" not in quart.session or "credentials" not in quart.session:
            # Create a new state and credentials session
            quart.session["state"] = None
            quart.session["credentials"] = None

        # Render the homepage
        return await quart.render_template("index.html")

    async def _handle_route_callback(self) -> str:
        # Retrieve the OAuth state
        oauth_state: Final[str] = quart.session.get("state")

        # Create a new OAuth control flow
        oauth_control_flow: Final[Flow] = Flow.from_client_secrets_file(
            "keys.json",
            state=oauth_state,
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        )

        # Configure the control flow
        oauth_control_flow.redirect_uri = quart.url_for(
            "_handle_route_callback", _external=True
        )

        # Get the callback response
        oauth_response: Final[str] = quart.request.url
        oauth_control_flow.fetch_token(authorization_response=oauth_response)

        # Store the credentials in the session
        oauth_credentials = oauth_control_flow.credentials
        quart.session["credentials"] = {
            "token": oauth_credentials.token,
            "refresh_token": oauth_credentials.refresh_token,
            "token_uri": oauth_credentials.token_uri,
            "client_id": oauth_credentials.client_id,
            "client_secret": oauth_credentials.client_secret,
            "scopes": oauth_credentials.scopes,
        }

        # Redirect back to the home page
        return quart.redirect(quart.url_for("_handle_route_home"))

    async def _handle_route_websocket(self) -> str:
        try:
            while True:
                # Declare incoming data variable
                incoming_data: Final[dict] = await quart.websocket.receive_json()

                # Parse the message contents
                message_request_type: Final[str] = incoming_data.get("request_type")
                message_request_data: Final[str] = incoming_data.get("request_data")
                message_request_args: Final[dict] = incoming_data.get("request_args")
                message_transport_client_id: Final[str] = incoming_data.get("transport_client_id")

                # Client -> Server || Requesting data to hydrate/update the main webpage
                if message_request_type == "data":
                    # Client is requesting the current user's profile image
                    if message_request_data == "user-profile-image":
                        # Check if the current user is signed in
                        if quart.session.get("credentials") == None:
                            # User is not logged in
                            await quart.websocket.send_json(
                                {
                                    "response_type": message_request_type,
                                    "response_data": message_request_data,
                                    "response_args": message_request_args,
                                    "transport_client_id": message_transport_client_id,
                                }
                            )
                        else:

                            # Retrieve the stored credentials
                            credentials: Final[Credentials] = Credentials(**quart.session.get("credentials"))

                            # Build the PeopleAPI service
                            people_api_service: Final[any] = build("people", "v1", credentials=credentials)
                            results: Final[any] = (
                                people_api_service.people()
                                .get(resourceName="people/me", personFields="photos")
                                .execute()
                            )

                            # Return the user profile image
                            await quart.websocket.send_json(
                                {
                                    "response_type": message_request_type,
                                    "response_data": message_request_data,
                                    "response_args": results.get("photos")[0].get("url"),
                                    "transport_client_id": message_transport_client_id,
                                }
                            )

                # Client -> Server || Requesting an OAuth session to login a user
                if message_request_type == "oauth":
                    # Client is requesting to login/register a user
                    if message_request_data == "register":
                        # Generate an OAuth control flow
                        oauth_control_flow: Final[Flow] = Flow.from_client_secrets_file(
                            "keys.json",
                            scopes=[
                                "https://www.googleapis.com/auth/userinfo.profile",
                                "https://www.googleapis.com/auth/spreadsheets",
                            ],
                        )

                        # Configure the control flow
                        oauth_control_flow.redirect_uri = "http://127.0.0.1:5000/callback"

                        # Generate the OAuth URL and OAuth state
                        oauth_url, oauth_state = oauth_control_flow.authorization_url(
                            access_type="offline",
                            include_granted_scopes="true",
                            prompt="consent",
                        )

                        # Store the OAuth state in the current session
                        quart.session["state"] = oauth_state

                        # Prompt OAuth redirection
                        await quart.websocket.send_json(
                            {
                                "response_type": message_request_type,
                                "response_data": message_request_data,
                                "response_args": oauth_url,
                                "transport_client_id": message_transport_client_id,
                            }
                        )
        except CancelledError:
            raise

# Script Check
if __name__ == "__main__":
    # Run in debug mode
    Server({"SECRET_KEY": "ASTRL-DEV"}).run_app_as_debug()
