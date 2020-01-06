#!/bin/bash

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

install -Dm 755 powerswitch.py /usr/local/bin/powerswitch
install -Dm 644 powerswitch.service /usr/local/lib/systemd/system/powerswitch.service
