#!/usr/bin/env bash

sudo apt-get update -qq
sudo apt-get install dig -y
nosetests app/tests
