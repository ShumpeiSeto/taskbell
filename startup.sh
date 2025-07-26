#!/bin/bash

flask db init || true
flask db migrate || true
flask db upgrade

python server.py