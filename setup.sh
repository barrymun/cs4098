#!/usr/bin/env bash

sudo apt-get update

sudo apt-get upgrade -y

sudo apt-get -y install python-pip
pip install --upgrade pip

sudo apt-get install -y \
    tcl \
    tcl-dev \
    check \
    expect \
    libxml2 \
    flex \
    bison \
    byacc \
    python-dev \
    python3-dev \
    libreadline-dev \
    lib32ncurses5-dev

sudo apt-get update

sudo apt-get upgrade -y

sudo pip install -r requirements.txt

cd peos/

make

cd ../

bash pml_test.sh