#!/bin/bash

# GPIO 21 に出力
echo "21" | tee /sys/class/gpio/export
echo "out" | tee /sys/class/gpio/gpio21/direction

echo "0" | tee /sys/class/gpio/gpio21/value

echo "21" > /sys/class/gpio/unexport
