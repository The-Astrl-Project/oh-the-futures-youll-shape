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
from middleware.statistics import StatisticsMiddleware
from modules.bot import SearchUtils, SearchQuery, search
# ---
import quart
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
    _app: quart.Quart = None
    _quart_configuration: dict = None

    # Constructor
    def __init__(self, quart_configuration: dict) -> None:
        # Store the Quart configuration
        self._quart_configuration = quart_configuration

        # Instance a new Quart app
        self._app = quart.Quart(__name__)

        # Configure the Quart app
        self._app.config.update(self._quart_configuration)

        # Apply middleware
        self._app.asgi_app = StatisticsMiddleware(self._app.asgi_app)

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
        oauth_state: Final[str] = quart.session.get("state", None)

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
        oauth_control_flow.redirect_uri = quart.url_for("_handle_route_callback", _external=True)

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
        # Local method for handling the sending of websocket data
        async def send_as_json(response_type: str, response_data: str, response_args: dict, transport_client_id: str) -> None:
            await quart.websocket.send_json(
                {
                    "response_type": response_type,
                    "response_data": response_data,
                    "response_args": response_args,
                    "transport_client_id": transport_client_id,
                }
            )

        # Indefinitely poll for new websocket connections/data
        while True:
            # Retrieve incoming JSON
            incoming_data: Final[dict] = await quart.websocket.receive_json()

            # Data request or OAuth request?
            request_type: Final[str] = incoming_data.get("request_type", None)
            # What specific data are we looking for
            request_data: Final[str] = incoming_data.get("request_data", None)
            # Supplied information from the client/user
            request_args: Final[dict] = incoming_data.get("request_args", None)
            # The websockets UUID
            transport_client_id: Final[str] = incoming_data.get("transport_client_id", None)

            match request_type:
                case "data":
                    match request_data:
                        case "user-profile-image":
                            # Check if the current user is signed in
                            if quart.session.get("credentials", None) == None:
                                # User is not logged in
                                await send_as_json(
                                    response_type=request_type,
                                    response_data=request_data,
                                    response_args={"url": "../static/images/user_profile_fallback_icon.svg"},
                                    transport_client_id=transport_client_id,
                                )

                                # Next iteration
                                continue

                            # Retrieve stored credentials
                            credentials: Final[Credentials] = Credentials(**quart.session.get("credentials", None))

                            # Build the PeopleAPI service
                            people_api_service: Final[any] = build("people", "v1", credentials=credentials)

                            # Execute an API request
                            results: Final[any] = people_api_service.people().get(resourceName="people/me", personFields="photos").execute()

                            # Retrieve the image URL
                            image_url: Final[str] = results.get("photos", None)[0].get("url", "../static/images/user_profile_fallback_icon.svg")

                            # Return the user profile image
                            await send_as_json(
                                response_type=request_type,
                                response_data=request_data,
                                response_args={"url": image_url},
                                transport_client_id=transport_client_id,
                            )

                            # Next iteration
                            continue

                        case "search":
                            # Next iteration
                            continue

                        case "autocomplete":
                            # Run an autocomplete request on the given query
                            autocomplete_results: Final[list[str]] = SearchUtils.autocomplete_region_from_query(query=request_args.get("input", None))

                            # Check if a valid result was return
                            if autocomplete_results is None:
                                # Notify of invalid query
                                await send_as_json(
                                    response_type=request_type,
                                    response_data=request_data,
                                    response_args={"results": "Invalid!", "target": request_args.get("target", None)},
                                    transport_client_id=transport_client_id,
                                )

                                # Next iteration
                                continue

                            # Return autocomplete results
                            await send_as_json(
                                response_type=request_type,
                                response_data=request_data,
                                response_args={"results": f"{autocomplete_results[4]}, {autocomplete_results[2]}", "target": request_args.get("target", None)},
                                transport_client_id=transport_client_id,
                            )

                            # Next iteration
                            continue

                case "oauth":
                    match request_data:
                        case "user-register":
                            # Generate an OAuth control flow
                            oauth_control_flow: Final[Flow] = (
                                Flow.from_client_secrets_file(
                                    "keys.json",
                                    scopes=[
                                        "https://www.googleapis.com/auth/userinfo.profile",
                                        "https://www.googleapis.com/auth/spreadsheets",
                                    ],
                                )
                            )

                            # Configure the redirect uri
                            oauth_control_flow.redirect_uri = "http://127.0.0.1:5000/callback"

                            # Generate the OAuth url and Oauth state
                            oauth_control_flow_url, oauth_control_flow_state = (
                                oauth_control_flow.authorization_url(
                                    prompt="consent",
                                    access_type="offline",
                                    include_granted_scopes="true",
                                )
                            )

                            # Store the OAuth state in the current session
                            quart.session["state"] = oauth_control_flow_state

                            # Prompt OAuth control flow on the client
                            await send_as_json(
                                response_type=request_type,
                                response_data=request_data,
                                response_args={"url": oauth_control_flow_url},
                                transport_client_id=transport_client_id,
                            )

                            # Next iteration
                            continue

                        case "user-unregister":
                            # Next iteration
                            continue
                case _:
                    # Malformed or invalid request
                    continue

# Script Check
if __name__ == "__main__":
    # Run in debug mode
    Server({"SECRET_KEY": "ASTRL-DEV"}).run_app_as_debug()
