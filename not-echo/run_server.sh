#!/bin/bash
#
# We use a shell starter instead of dodo because dodo always does line-buffering.

uvicorn not-echo.server.main:app --reload --app-dir src
