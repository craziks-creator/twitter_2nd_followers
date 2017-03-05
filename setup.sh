#!/bin/bash
virtualenv env -p python2.7
env/bin/pip install -r requirements.txt
chmod u+x manage.py
