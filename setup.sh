#!/usr/bin/env bash

apt-get update -qq
apt-get install dig -y
nosetests app/tests
