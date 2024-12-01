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
import json
from os import mkdir
from typing import Final
# ---

# ---
import quart
# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || middleware/statistics.py
#
# Responsible for handling statistical data.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------


# Class Definitions
class StatisticsMiddleware:
    # Enums

    # Interfaces

    # Constants

    # Public Variables

    # Private Variables
    _quart_app: quart.Quart
    _log_file_name: str
    _stats_data_dict: dict
    _is_running: bool = False

    # Constructor
    def __init__(self, quart_app: quart.Quart, log_file_name: str = "./logs/stats.json") -> None:
        # Store middleware configuration
        self._quart_app = quart_app
        self._log_file_name = log_file_name

        # Try to create the logging directory and file
        try:
            # Create the logging directory
            mkdir("./logs")

            # Create the logging file
            with open("./logs/stats.json", "a") as log_file:
                # To avoid parsing errors
                log_file.write('{"routes": {}, "addresses": {}, "args": {}}')

                # Close the log file
                log_file.close()
        except:
            # Already created so just skip ahead
            pass

        # Load the previous log file
        with open(self._log_file_name, "r") as log_file:

            # Load the data
            self._stats_data_dict = json.load(log_file)

            # Close the file
            log_file.close()

    async def __call__(self, scope, receive, send) -> None:
        # Collect the IP address
        request_address: Final[str] = scope.get("client", None)[0]

        # Collect the route
        request_route: Final[str] = scope.get("path", None)

        # Update the stats dict
        self._stats_data_dict["routes"][request_route] = (
            1
            + self._stats_data_dict.get("routes", None)
            .get(request_route, 0)
        )
        self._stats_data_dict["addresses"][request_address] = (
            1
            + self._stats_data_dict.get("routes", None)
            .get(request_address, 0)
        )

        # Collect the passed args and update their values
        request_args_list: Final[list[str]] = (
            scope.get("query_string", None)
            .decode("utf-8")
            .split("&")
        )

        for request_arg in request_args_list:
            # Check if any args were sent in the request
            if len(request_arg) == 0:
                # No args to parse || Exit
                break

            # Retrieve the arg name and arg value
            arg_name: Final[str] = request_arg.split("=")[0]
            arg_value: Final[str] = request_arg.split("=")[1]

            # Update
            self._stats_data_dict["args"][arg_name] = {
                arg_value: 1
                + self._stats_data_dict.get("args", None)
                .get(arg_name, {arg_value: 0})
                .get(arg_value, 0)
            }

        # Log statistics to the console
        print(f"[STATS] IP: {request_address}, Route: {request_route}, Route Hits: {self._stats_data_dict['routes'][request_route]}")

        # Iterate through the args list
        for request_arg in request_args_list:
            # Sanity check
            if len(request_arg) == 0:
                break

            # Retrieve the arg name and arg value
            arg_name: Final[str] = request_arg.split("=")[0]
            arg_value: Final[str] = request_arg.split("=")[1]

            print(f"[STATS] Arg: {arg_name}={arg_value}, Hits: {self._stats_data_dict['args'][arg_name][arg_value]}")

        # Open the log file
        with open(self._log_file_name, "w") as log_file:
            # Dump data into a JSON file
            json.dump(self._stats_data_dict, log_file)

            # Close the file
            log_file.close()

        # Return the response
        return await self._quart_app(scope=scope, receive=receive, send=send)

    # Public Static Methods

    # Public Inherited Methods

    # Private Static Methods

    # Private Inherited Methods
