#!/usr/bin/env bash

sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get -y install python-pip
pip install --upgrade pip
pip install env \
    venv

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

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo service mongod start

sudo apt-get update
sudo apt-get upgrade -y

pip install -r requirements.txt

cd peos/

make

cd ../

bash pml_test.sh