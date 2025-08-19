#!/bin/bash

TYPE=$1
ENDPOINT=$2
CALL_BODY=$3

curl -X $TYPE "$(cat api_url.txt)/$ENDPOINT" -d "$(cat api_call_bodies/$CALL_BODY)"