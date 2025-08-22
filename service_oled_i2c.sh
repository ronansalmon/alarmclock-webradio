#!/bin/bash
DIR="$( dirname -- "${BASH_SOURCE[0]}"; )";
cd ${DIR}

source /app/python/bin/activate
while true; do
  python oled_handler_i2c.py
  sleep 2
done


