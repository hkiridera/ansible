#!/bin/bash

# GPIO 20 に出力
#echo "20" | tee /sys/class/gpio/export
#echo "out" | tee /sys/class/gpio/gpio20/direction

echo "0" | tee /sys/class/gpio/gpio20/value
echo "20" > /sys/class/gpio/unexport
