#!/bin/bash

# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

VIRTUAL_ENV="/home/pi/Projects/Garage_Temp_Log/gt_env"
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

echo $PATH

python
