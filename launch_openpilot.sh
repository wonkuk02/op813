#!/usr/bin/bash

export PASSIVE="0"
chmod 700 ./unix.sh
chmod 700 ./launch_chffrplus.sh
sed -i -e 's/\r$//' ./launch_chffrplus.sh
sed -i -e 's/\r$//' ./unix.sh
exec ./launch_chffrplus.sh

