#!/bin/bash
sudo apt-get update
sudo apt-get install -y python-opencv  libopencv-dev motion
sudo cp motion.conf /etc/motion/motion.conf
sudo pip install slacker
