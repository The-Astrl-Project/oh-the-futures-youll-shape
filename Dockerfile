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

# 3.12 || Alpine Linux
FROM python:3.12.8-alpine3.20 as build

# Copy the source directory
COPY ./src/ /app

# Setup the Python environment
RUN pip3 install --upgrade -r /app/requirements.txt && pyppeteer-install

# Expose volumes
VOLUME [ "/app/keys" ]
VOLUME [ "/app/logs" ]
VOLUME [ "/app/certs" ]

# Expose HTTPS port
EXPOSE 443/tcp

# Configure the system environment
ENV SECRET_KEY="SECRET_KEY"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD [ "curl -f https://astrl.dev/healthcheck || exit 1" ]

# Execute
CMD [ "python3", "/app/prod.py" ]
