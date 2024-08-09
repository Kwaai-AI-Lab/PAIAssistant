#!/bin/bash

if ! test -f /pai/api/index/index.complete; then
    cd /pai/api
    python createindex.py
fi
npm start --prefix /pai/web &
cd /pai/api
python api.py &

wait -n
exit $?
