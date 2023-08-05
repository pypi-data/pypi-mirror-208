#!/bin/sh

# These are pretty hacky and need to be cleaned up, but serve a purpose.

# Set REAL_TESTING_TOKEN for more tests.

set -ex

export SPORESTACK_ENDPOINT=https://api.sporestack.com
# export SPORESTACK_ENDPOINT=http://127.0.0.1:8000

export SPORESTACK_DIR=$(pwd)/dummydotsporestackfolder

rm -r $SPORESTACK_DIR || true
mkdir $SPORESTACK_DIR

sporestack version
sporestack version | grep '[0-9]\.[0-9]\.[0-9]'

sporestack api-endpoint
sporestack api-endpoint | grep "$SPORESTACK_ENDPOINT"

sporestack token list
sporestack token list 2>&1 | wc -l | grep '2$'

sporestack token import importediminvalid --key "imaninvalidkey"
sporestack token list | grep importediminvalid
sporestack token list | grep imaninvalidkey
sporestack server launch --no-quote --token neverbeencreated --operating-system debian-11 --days 1 2>&1 | grep 'does not exist'

# Online tests start here.

sporestack token create --dollars 50 --currency fakecurrency ihaveafakecurrency 2>&1 | grep 'value is not a valid'
sporestack server launch --no-quote --token importediminvalid --operating-system debian-11 --days 1 2>&1 | grep 'ensure this value has at least 32'

sporestack server flavors | grep vcpu
sporestack server operating-systems | grep debian-11
sporestack server regions | grep sfo3

if [ -z "$REAL_TESTING_TOKEN" ]; then
	rm -r $SPORESTACK_DIR
	echo "REAL_TESTING_TOKEN not set, not finishing tests."
	echo Success
	exit 0
else
	echo "REAL_TESTING_TOKEN is set, will continue testing."
fi

sporestack token import realtestingtoken --key "$REAL_TESTING_TOKEN"
sporestack token balance realtestingtoken | grep -F '$'
sporestack token info realtestingtoken
sporestack token messages realtestingtoken
sporestack token servers realtestingtoken

sporestack server list --token realtestingtoken
sporestack server launch --no-quote --token realtestingtoken --operating-system debian-11 --days 1 --hostname sporestackpythonintegrationtestdelme
sporestack server list --token realtestingtoken | grep sporestackpythonintegrationtestdelme
sporestack server topup --token realtestingtoken --hostname sporestackpythonintegrationtestdelme --days 1
sporestack server info --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server json --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server autorenew-enable --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server autorenew-disable --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server start --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server stop --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server rebuild --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server delete --token realtestingtoken --hostname sporestackpythonintegrationtestdelme
sporestack server forget --token realtestingtoken --hostname sporestackpythonintegrationtestdelme

rm -r $SPORESTACK_DIR

echo Success
