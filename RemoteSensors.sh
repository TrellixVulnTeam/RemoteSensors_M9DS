#! /bin/bash

read -p 'IP: ' ipvar
read -p 'Username: ' uservar
read -sp 'Password: ' passvar


./venv/bin/python main.py $ipvar $uservar $passvar
