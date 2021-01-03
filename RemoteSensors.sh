#! /bin/bash

read -p 'IP: ' ipvar
read -p 'Username: ' uservar
read -sp 'Password: ' passvar

source ./venv/bin/activate
# virtualenv is now active.
#
python main.py $ipvar $uservar $passvar
