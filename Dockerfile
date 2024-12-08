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

# Setup the Debian environment
RUN apt-get update && apt-get install gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget libcairo-gobject2 libxinerama1 libgtk2.0-0 libpangoft2-1.0-0 libthai0 libpixman-1-0 libxcb-render0 libharfbuzz0b libdatrie1 libgraphite2-3 libgbm1 -y

# Install Chromium
RUN pyppeteer-install

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
CMD [ "/usr/bin/env", "bash", "./prod.sh" ]
