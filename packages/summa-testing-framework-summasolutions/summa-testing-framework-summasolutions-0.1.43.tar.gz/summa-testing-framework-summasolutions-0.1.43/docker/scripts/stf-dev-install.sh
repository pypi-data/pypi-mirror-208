#!/bin/bash
cd /stf
/usr/local/bin/pip3 install --editable .
cd /app

exec "$@"