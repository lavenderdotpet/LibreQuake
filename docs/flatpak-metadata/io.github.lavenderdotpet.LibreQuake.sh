#!/bin/bash
ENGINE_CONFIG="${XDG_CONFIG_HOME}/lq_engine"
HIDE_LAUNCHER="${XDG_CONFIG_HOME}/lq_hide_launcher"

function write_engine_config {
    if [[ -f ${ENGINE_CONFIG} ]]; then
      rm "${ENGINE_CONFIG}"
    fi
    echo "$1" > "${ENGINE_CONFIG}"
}

if [[ ! -f "${HIDE_LAUNCHER}" ]]; then

#     FALSE "fteqw (Multiplayer)" \
#     FALSE "vkQuake (Vulkan renderer)" \

  CHOICE=$(zenity --list --radiolist --hide-header --modal --width=600 --height=400 \
    --column="" --column="" \
    TRUE "Ironwail (Default)" \
    FALSE "QuakeSpasm (Basic modern engine)" \
    FALSE "QSS-M (OpenGL 1.x/2.x for older hardware)" \
    --title "LibreQuake Launcher" \
    --text "Select which engine to launch" \
    --extra-button "Open user content directory" \
    --ok-label "Launch" \
    --cancel-label "Quit" \
    --window-icon "/app/share/icons/hicolor/scalable/apps/io.github.lavenderdotpet.LibreQuake.svg")

  case "$CHOICE" in
    "Open user content directory")
      io.github.lavenderdotpet.LibreQuake.open-userdir.sh
      exit 2
      ;;
    "QuakeSpasm"*)
      write_engine_config "quakespasm"
      ;;
    "Ironwail"*)
      write_engine_config "ironwail"
      ;;
    "vkQuake"*)
      write_engine_config "vkquake"
      ;;
    "fteqw"*)
      write_engine_config "fteqw"
      ;;
    "QSS-M"*)
      write_engine_config "qssm"
      ;;
    *)
      exit 1
      ;;
  esac
  touch "${HIDE_LAUNCHER}"
fi

exitcode=$?
if [[ $exitcode -ne 0 ]]; then
  echo "Quitting..."
elif [[ $exitcode -eq 0 ]]; then
  if [[ -f "/app/bin/$1" ]]; then
    ENGINE="$1"
    GAME_ARGS="${@:2}"
  else
    ENGINE=$(cat "${ENGINE_CONFIG}")
    GAME_ARGS="$@"
  fi
  echo "Launching LibreQuake using ${ENGINE} ${GAME_ARGS}..."
  ${ENGINE} -basedir /app/share/games/librequake ${GAME_ARGS}
  # Once engines start merging the -userdir update from QuakeSpasm, we can use it instead of engine patches
  # ${ENGINE} -basedir /app/share/games/librequake -userdir ${XDG_DATA_HOME} ${GAME_ARGS}
fi
