#!/bin/bash
echo "デプロイ開始"

export FLASK_APP=taskbell 

# flask db init || true
flask db migrate -m "Auto migration" || true
flask db upgrade

python server.py