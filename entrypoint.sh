#!/bin/bash

NB_CORES=$(grep processor /proc/cpuinfo | wc -l)

gunicorn --bind "0.0.0.0:$PORT" \
    --worker-class uvicorn.workers.UvicornWorker  \
    --max-requests="$MAX_REQUESTS" \
    --max-requests-jitter="$MAX_REQUESTS_JITTER" \
    --timeout=20  \
    --workers=$(( 2 * NB_CORES + 1 )) \
    app.main:app