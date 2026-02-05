if [ ${DEV_VM} == 1 ]; then
    export SUBMISSION_URL='http://localhost:1511'
    export SUBMISSION_PORT=1511
    export DATABASE_PORT=16442
    export WEBSOCKET_PORT=8443
fi
