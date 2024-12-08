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
# ---
from app import Server
# ---
import uvloop
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || prod.py
#
# Launches a production ready instance.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants

# Public Variables

# Private Variables

# main
def main() -> None:
    # Create a new config object
    config = Config()

    # Bind on the IPv4 to port 443
    config.bind = ["0.0.0.0:443"]

    # Cloudflare Origin CA
    config.keyfile = "./certs/astrl.dev.key"
    config.ca_certs = "./certs/astrl.dev.pem"
    config.certfile = "./certs/astrl.dev.pem"

    # Configure number of available workers
    config.workers = 16
    config.worker_class = "uvloop"

    # Install uvloop
    uvloop.install()

    # Run the app
    asyncio.run(serve(Server({"SECRET_KEY": f"{environ['SECRET_KEY']}", "IS_PROD": True}).return_app_instance(), config, mode="asgi"))

# Public Methods

# Private Methods

# Script Check
if __name__ == "__main__":
    main()
