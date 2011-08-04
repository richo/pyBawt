#!/bin/sh

codedir=`dirname $0`

cd $codedir

screen -dmS pyBawt python2.7 $codedir/pyBawt.py
