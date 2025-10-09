#!/bin/bash
#
# We use a shell starter instead of dodo because dodo always does line-buffering.

uvicorn n-clients.server.main:app --reload --app-dir src
