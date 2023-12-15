#!/bin/bash
DIR="$( dirname -- "${BASH_SOURCE[0]}"; )";
cd ${DIR}

source  ~/python/bin/activate
while true; do
  python oled_handler.py
  sleep 2
done


