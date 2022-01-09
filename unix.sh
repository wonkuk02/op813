#!/usr/bin/bash

  mount -o rw,remount /system

  sed -i 's/self._AWARENESS_TIME = 35/self._AWARENESS_TIME = 10800/' ./selfdrive/monitoring/driver_monitor.py
  sed -i 's/self._DISTRACTED_TIME = 11/self._DISTRACTED_TIME = 7200/' ./selfdrive/monitoring/driver_monitor.py
  sed -i 's/self.face_detected = False/self.face_detected = True/' ./selfdrive/monitoring/driver_monitor.py
  sed -i 's/self.face_detected = driver/self.face_detected = True # driver/' ./selfdrive/monitoring/driver_monitor.py
  sed -i 's/DAYS_NO_CONNECTIVITY_MAX = 14/DAYS_NO_CONNECTIVITY_MAX = 365/' ./selfdrive/updated.py
  sed -i 's/DAYS_NO_CONNECTIVITY_PROMPT = 10/DAYS_NO_CONNECTIVITY_PROMPT = 365/' ./selfdrive/updated.py
  chmod 700 ./t.sh
  chmod 700 ./unix.sh
  chmod 700 ./tune.py
  chmod 744 /system/media/bootanimation.zip
  chmod 700 ./selfdrive/ui/qt/spinner
  chmod 700 ./selfdrive/ui/soundd/soundd
  chmod 700 ./selfdrive/ui/soundd/sound.*
  chmod 700 ./scripts/*.sh
  sed -i -e 's/\r$//' ./*.py
  sed -i -e 's/\r$//' ./selfdrive/*.py
  sed -i -e 's/\r$//' ./selfdrive/manager/*.py
  sed -i -e 's/\r$//' ./selfdrive/car/*.py
  sed -i -e 's/\r$//' ./selfdrive/ui/*.cc
  sed -i -e 's/\r$//' ./selfdrive/ui/*.h
  sed -i -e 's/\r$//' ./selfdrive/controls/*.py
  sed -i -e 's/\r$//' ./selfdrive/controls/lib/*.py
  sed -i -e 's/\r$//' ./selfdrive/locationd/models/*.py
  sed -i -e 's/\r$//' ./cereal/*.py
  sed -i -e 's/\r$//' ./cereal/*.capnp
  sed -i -e 's/\r$//' ./selfdrive/car/gm/*.py
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/*.cc
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/*.h
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/offroad/*.cc
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/widgets/*.cc
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/offroad/*.h
  sed -i -e 's/\r$//' ./selfdrive/ui/qt/widgets/*.h
  sed -i -e 's/\r$//' ./selfdrive/ui/soundd/*.cc
  sed -i -e 's/\r$//' ./selfdrive/ui/soundd/*.h
  sed -i -e 's/\r$//' ./selfdrive/boardd/*.cc
  sed -i -e 's/\r$//' ./selfdrive/boardd/*.pyx
  sed -i -e 's/\r$//' ./selfdrive/boardd/*.h
  sed -i -e 's/\r$//' ./selfdrive/boardd/*.py
  sed -i -e 's/\r$//' ./selfdrive/camerad/cameras/*.h
  sed -i -e 's/\r$//' ./selfdrive/camerad/cameras/*.cc
  sed -i -e 's/\r$//' ./selfdrive/camerad/snapshot/*.py
  sed -i -e 's/\r$//' ./selfdrive/camerad/*.cc
  sed -i -e 's/\r$//' ./selfdrive/thermald/*.py
  sed -i -e 's/\r$//' ./selfdrive/athena/*.py
  sed -i -e 's/\r$//' ./scripts/*.sh
  sed -i -e 's/\r$//' ./common/*.py
  sed -i -e 's/\r$//' ./common/*.pyx
  sed -i -e 's/\r$//' ./launch_env.sh
  sed -i -e 's/\r$//' ./launch_openpilot.sh
  sed -i -e 's/\r$//' ./Jenkinsfile
  sed -i -e 's/\r$//' ./SConstruct
  sed -i -e 's/\r$//' ./t.sh
