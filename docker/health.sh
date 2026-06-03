#!/bin/bash

Heartbeat() {
  local -r ALIVE=0 DEAD=1

  if [ ! -z $(pgrep -fl "\.py" > /dev/null) ]; then
    exit $ALIVE
  else
    exit $DEAD
  fi
}

Heartbeat