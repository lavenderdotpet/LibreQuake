#!/bin/bash
HIDE_LAUNCHER="${XDG_CONFIG_HOME}/lq_hide_launcher"
if [[ -f "${HIDE_LAUNCHER}" ]]; then
  rm "${HIDE_LAUNCHER}"
fi
io.github.lavenderdotpet.LibreQuake.sh $@
