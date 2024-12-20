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
RUN apt-get update && apt-get install ca-certificates fonts-liberation gconf-service libappindicator1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo-gobject2 libcairo2 libcups2 libdatrie1 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgraphite2-3 libgtk-3-0 libgtk2.0-0 libharfbuzz0b libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 libstdc++6 libthai0 libx11-6 libx11-xcb1 libxcb-render0 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxinerama1 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils -y

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
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD [ "wget --no-verbose --tries=1 --spider https://astrl.dev/healthcheck || exit 1" ]

# Execute
CMD [ "/usr/bin/env", "bash", "./prod.sh" ]
