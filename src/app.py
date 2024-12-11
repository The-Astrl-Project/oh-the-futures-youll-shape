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
from random import randint
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
    """A minimal and asynchronous webserver."""

    # Enums

    # Interfaces

    # Constants
    __version__: Final[str] = "0.5.3-DEV"

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

        # Server configuration
        self._app.errorhandler(404)(self._handle_client_error)
        self._app.before_request((self._handle_before_request))

        # Astrl legal
        self._app.route("/legal/tos", methods=["GET"])(self._handle_tos)
        self._app.route("/legal/privacy", methods=["GET"])(self._handle_privacy)

        # Web app routes
        self._app.route("/my-future", methods=["GET"])(self._handle_route_home)
        self._app.route("/callback", methods=["GET"])(self._handle_route_callback)
        self._app.websocket("/transport")(self._handle_route_websocket)

    # Public Static Methods

    # Public Inherited Methods
    def run_app_as_debug(self) -> None:
        """Launches the Quart app with debugging enabled."""

        # Configure the environment
        environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Start the web server
        self._app.run(host="0.0.0.0", port="5000", debug=True, use_reloader=False)

    def return_app_instance(self) -> quart.Quart:
        """Returns the Quart app instance."""

        # Return the quart instance
        return self._app

    # Private Static Methods

    # Private Inherited Methods
    async def _util_write_to_sheet(self, return_data: dict, target_state: str, current_state: str) -> str:
        """
        Writes the scrapped data into a Google Sheet for user consumption. Returns
        the Google Sheet URL

        Parameters
        ----------
        return_data : dict
            The scrapped web data

        target_state : str
            The target state

        current_state : str
            The current state
        """

        # Retrieve stored credentials
        credentials: Final[Credentials] = Credentials(**quart.session.get("credentials", None))

        # Build the Google Sheets API service
        sheets_service = build("sheets", "v4", credentials=credentials)

        # Create a new sheet and store the resulting ID
        body: Final[dict] = {"properties": {"title": f"Oh, the Futures You'll Shape in {target_state}"}}
        sheet_id = (
            sheets_service.spreadsheets()
            .create(body=body, fields="spreadsheetId")
            .execute()
            .get("spreadsheetId", None)
        )

        # Parse the return data into topics
        data_topics: Final[list[str]] = return_data.keys()

        # Iterate through each topic
        for data in data_topics:
            # Retrieve the target state and current state entries
            state_topics: Final[list[str]] = return_data[data].keys()

            # Iterate through each state topic
            for state in state_topics:
                # Local generate function declaration
                async def _generate() -> list[dict]:
                    """
                    Generates a Google Sheet Page for every data source.
                    Each page generated is one atomic request
                    """

                    # Declare return data
                    request_data: list[dict] = []

                    # Iterate through each data source
                    for source in return_data[data][state].keys():

                        # Check for invalid data
                        if return_data[data][state][source] is None:
                            # Continue to the next row
                            continue

                        # Check if this row has any applicable data
                        if len(return_data[data][state][source]) == 0:
                            # Continue to the next row
                            continue

                        # Create a page id
                        page_id: Final[int] = randint(0, 9999)

                        # Format data sources
                        formatted_data_title: Final[str] = data.replace("_", " ").title()
                        formatted_state_title: Final[str] = (
                            target_state.replace("_", " ").title()
                            if state == "target_state"
                            else current_state.replace("_", " ").title()
                        )
                        formatted_source_title: Final[str] = source.replace("_", " ").title()

                        # Create a new sheet
                        request_data.append(
                            {
                                "addSheet": {
                                    "properties": {
                                        "title": f"{formatted_data_title} - {formatted_state_title} - {formatted_source_title}",
                                        "sheetId": page_id,
                                    },
                                },
                            }
                        )

                        # Modify the sheet dimensions
                        request_data.append(
                            {
                                "appendDimension": {
                                    "sheetId": page_id,
                                    "dimension": "COLUMNS",
                                    "length": 20,
                                },
                            }
                        )
                        request_data.append(
                            {
                                "appendDimension": {
                                    "sheetId": page_id,
                                    "dimension": "ROWS",
                                    "length": 120,
                                },
                            }
                        )

                        # Declare the column index
                        column_index: int = 0

                        # Iterate through each key
                        for key in return_data[data][state][source][0].keys():
                            # Declare the row index
                            row_index: int = 1

                            # Create a new request
                            request_data.append(
                                {
                                    "updateCells": {
                                        "start": {
                                            "sheetId": page_id,
                                            "rowIndex": 0,
                                            "columnIndex": column_index,
                                        },
                                        "rows": [
                                            {
                                                "values": [
                                                    {
                                                        "userEnteredValue": {
                                                            "stringValue": key.replace(
                                                                "_", " "
                                                            ).title()
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        "fields": "userEnteredValue",
                                    }
                                }
                            )

                            # Collect the available entries
                            entries: Final[list[dict]] = return_data[data][state][source]

                            # Iterate
                            for entry in entries:
                                # Create a new request
                                request_data.append(
                                    {
                                        "updateCells": {
                                            "start": {
                                                "sheetId": page_id,
                                                "rowIndex": row_index,
                                                "columnIndex": column_index,
                                            },
                                            "rows": [
                                                {
                                                    "values": [
                                                        {
                                                            "userEnteredValue": {
                                                                "stringValue": entry[key]
                                                            }
                                                        }
                                                    ]
                                                }
                                            ],
                                            "fields": "userEnteredValue",
                                        }
                                    }
                                )

                                # Increment the column index
                                row_index += 1

                            # Increment the row index
                            column_index += 1

                    # Return the generated body
                    return request_data

                # Generate the body
                body: Final[list[dict]] = await _generate()

                # Skip empty requests
                if len(body) == 0:
                    # Next row
                    continue

                # Submit a request
                sheets_service.spreadsheets().batchUpdate(body={"requests": body}, spreadsheetId=sheet_id).execute()

        # Return the Google Sheet URL
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

    async def _handle_client_error(self, _) -> str:
        # Redirect back to the home page
        return quart.redirect(quart.url_for("_handle_route_home"))

    async def _handle_before_request(self) -> None:
        # Make sessions permanent
        quart.session.permanent = True

    async def _handle_tos(self) -> str:
        # Render the TOS
        return await quart.render_template("terms.html")

    async def _handle_privacy(self) -> str:
        # Render the privacy policy
        return await quart.render_template("privacy.html")

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
            "./keys/keys.json",
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
                            results: Final[any] = (
                                people_api_service.people()
                                .get(resourceName="people/me", personFields="photos")
                                .execute()
                            )

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
                            # Check if the current user is signed in
                            if quart.session.get("credentials", None) == None:
                                # User is not logged in
                                await send_as_json(
                                    response_type=request_type,
                                    response_data=request_data,
                                    response_args={"response": "INVALID_SESSION"},
                                    transport_client_id=transport_client_id,
                                )

                                # Next iteration
                                continue

                            # User is logged in
                            await send_as_json(
                                response_type=request_type,
                                response_data=request_data,
                                response_args={"response": "PROCESSING_REQUEST"},
                                transport_client_id=transport_client_id,
                            )

                            # Extract the individual SearchQuery parameters
                            target_state: Final[str] = request_args.get("target_state", None)
                            current_state: Final[str] = request_args.get("current_state", None)
                            majoring_target: Final[str] = request_args.get("majoring_target", None)
                            use_queer_scoring: Final[str] = request_args.get("use_queer_scoring", None)

                            # Send a search request
                            response: Final[dict] = await search(
                                SearchQuery(
                                    target_state=target_state,
                                    current_state=current_state,
                                    majoring_target=majoring_target,
                                    use_queer_scoring=use_queer_scoring,
                                )
                            )

                            # Write the data into a Google Sheet
                            sheet_url: Final[str] = await self._util_write_to_sheet(
                                return_data=response,
                                target_state=target_state,
                                current_state=current_state,
                            )

                            # Notify the user
                            await send_as_json(
                                response_type=request_type,
                                response_data=request_data,
                                response_args={"response": "PROCESSING_FINISHED", "url": sheet_url},
                                transport_client_id=transport_client_id,
                            )

                        case "autocomplete":
                            # Check if an empty string was sent
                            if len(request_args.get("input", "").strip()) == 0:
                                # Don't even bother to parse
                                continue

                            # Declare the autocomplete results
                            autocomplete_results: str = None

                            # Check if the major or state should be auto-completed
                            if request_args.get("target", None) == "majoring-target":
                                # Major autocomplete
                                autocomplete_results = (
                                    SearchUtils.autocomplete_major_from_query(
                                        query=request_args.get("input", None)
                                    )
                                )
                            else:
                                # Autocomplete the region
                                region: Final[list[str]] = SearchUtils.autocomplete_region_from_query(query=request_args.get("input", None))

                                # Parse and format the data
                                autocomplete_results = f"{region[4]}, {region[2]}"

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
                                response_args={"results": autocomplete_results, "target": request_args.get("target", None)},
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
                                    "./keys/keys.json",
                                    scopes=[
                                        "https://www.googleapis.com/auth/userinfo.profile",
                                        "https://www.googleapis.com/auth/spreadsheets",
                                    ],
                                )
                            )


                            # Grab the value of is_prod
                            use_production_uri: Final[bool] = self._quart_configuration.get("IS_PROD")

                            # Check if we're in production or development
                            if use_production_uri == True:
                                # Use the production redirect
                                oauth_control_flow.redirect_uri = "https://astrl.dev/callback"
                            else:
                                # Use the development redirect
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
    Server({"SECRET_KEY": "ASTRL-DEV", "IS_PROD": False}).run_app_as_debug()

# Production ready app instance
prod: Final[quart.Quart] = Server({"SECRET_KEY": f"{environ['SECRET_KEY']}", "IS_PROD": True}).return_app_instance()
