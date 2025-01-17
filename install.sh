#!/bin/bash

printf "%s\n" "
###############################################################################
#   This script installs EOSFactory. It needs to be executed from within
#   the 'amaxfactory' folder.
#   This file was downloaded from https://github.com/tokenika/amaxfactory
###############################################################################
"

printf "%s" "
Installing 'amaxfactory' package locally with the Python pip system...
"

###############################################################################
# It is essential that the package is installed as a symlink, with
# the flag '-e'
###############################################################################
pip3 install --user -e .
chmod a+x amaxfactory/pythonmd.sh

printf "%s\n" "
Configuring the amaxfactory installation...
"

python3 amaxfactory/install.py

printf "%s\n" "
Verifying dependencies of EOSFactory...
"
python3 -m amaxfactory.config --dependencies
ret=$?
if [ $ret -ne 0 ]; then
    exit $ret
fi
printf "%s\n" "
OK
"

txtbld=$(tput bold)
bldred=${txtbld}$(tput setaf 1)
txtrst=$(tput sgr0)
printf "${bldred}%s${txtrst}" "
         ______         _____ _______ ____  _______     __
        |  ____  /\    / ____|__   __/ __ \|  __ \ \   / /
        | |__   /  \  | |       | | | |  | | |__) \ \_/ /
        |  __  / /\ \ | |       | | | |  | |  _  / \   /
        | |   / ____ \  |____   | | | |__| | | \ \  | |
        |_|  /_/    \_\ _____|  |_|  \____/|_|  \_\ |_|
"
printf "%s\n" "
To verify EOSFactory installation navigate to the 'amaxfactory' folder and run
these tests:
"
printf "%s\n" "
    $ python3 tests/hello_world.py
    $ python3 tests/eosio_token.py
    $ python3 tests/tic_tac_toe.py
"
