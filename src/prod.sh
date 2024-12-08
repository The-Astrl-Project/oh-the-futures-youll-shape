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

# Shebang
#!/usr/bin/env bash

# Execute
hypercorn \
--bind '0.0.0.0:443' \
--keyfile './certs/astrl.dev.key' \
--ca-certs './certs/astrl.dev.pem' \
--certfile './certs/astrl.dev.pem' \
--workers '16' \
--worker-class 'uvloop' \
asgi:app:prod
