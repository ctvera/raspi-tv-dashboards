#!/bin/bash
cat /home/pi/cecOut | /home/pi/cecremote.sh &
/home/pi/pipe_reader.py | cec-client > /home/pi/cecOut &

