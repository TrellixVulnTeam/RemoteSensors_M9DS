#! /bin/bash

rows=$(tput lines)
cols=$(tput cols)

MIN_ROWS=25
MIN_COLS=115

if [[ $rows -lt $MIN_ROWS || $cols -lt $MIN_COLS ]]
then
  echo Terminal size needs to be at least $MIN_ROWS lines x $MIN_COLS columns
  exit 1
fi

read -p '   IP: ' ipvar
read -p '   Username: ' uservar
read -sp '   Password: ' passvar


./venv/bin/python main.py "$ipvar" "$uservar" "$passvar"