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

# 3.12 || Debian Bookworm Slim
FROM python:3.12.8-slim-bookworm

# Set the working directory
WORKDIR /app

# Copy the source directory
COPY ./src/ .

# Setup the Python environment
RUN pip3 install --upgrade -r ./requirements.txt

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
CMD [ "python3", "prod.py" ]
