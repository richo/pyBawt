#!/bin/sh

cwd=`dirname $0`
cd $cwd

# Checkout master, shouldn't ever be broken
while echo; do
    echo "Starting fetch"

    git fetch
    git reset --hard origin/master
    echo "Starting pyBawt"
    ./pyBawt.py
    echo "pyBawt died, sleeping"
    sleep 5
done
