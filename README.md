WIP: alarmclock-webradio
===================

GPIO pin-outs MAX7219 Devices (SPI) (not used)
----------------------------------------------

| Board Pin    | Name        | RPi Pin   | RPi Function
| :----------: | :-----:     | --------: | :-----------
|          VDD | +3V Power   | 1        | 3V0 
|          VSS |  Ground     | 6        | GND 
|          SDA |  Data In    | 19       | GPIO 10 (MOSI)
|          CS  |  Chip Select| 24       | GPIO 8 (SPI CE0)
|          CLK |  Clock      | 23       | GPIO 11 (SPI CLK)
|          DC  |  Data/Comman| 22       | GPIO 25
|          RES |  RESET      | 18       | GPIO 24


GPIO pin-outs rotary volume
----------------------------------------------

| Board Pin    | Name        | RPi Pin   | RPi Function | test
| :----------: | :-----:      | --------: | :---------:
|          VCC | +3V Power   | 1        | 3V0           |
|          GND |  Ground     | 6        | GND           |
|          SW  |  Data In    | 29       | GPIO 5    | button
|          DT  |  Data In    | 31       | GPIO 6    | pin_a
|          CLK |  Data In    | 33       | GPIO 13   | pin_b

GPIO pin-outs rotary menu
----------------------------------------------


| Board Pin    | Name        | RPi Pin   | RPi Function
| :----------: | :-----:      | --------: | :-----------
|          VCC | +5V Power   | 4        | 5V0 
|          GND |  Ground     | 6        | GND 
|          SW  |  Data In    | 11       | GPIO 17
|          DT  |  Data In    | 13       | GPIO 27
|          CLK |  Data In    | 15       | GPIO 22


GPIO pin-outs Oled
----------------------------------------------

| Board Pin    | Name        | RPi Pin   | RPi Function
| :----------: | :-----:      | --------: | :-----------
|          VCC | +5V Power   | 4        | 5V0 
|          GND |  Ground     | 6        | GND 
|          SCL |  Data In    | 5        | GPIO 3 (SCL)
|          SDA |  Data In    | 3        | GPIO 2 (SDA)


usermod -a -G spi,gpio,i2c pi


# get current volume
amixer scontents
# init volume
amixer -q sset PCM '90%'
# test radio
ffplay -autoexit -nodisp -hide_banner -loglevel error http://spoonradio.ice.infomaniak.ch/spoonradio-hd &
# lower down volume
amixer -q sset PCM '100%-'

# restart all

sudo systemctl restart alarmclock_oled
sudo systemctl restart alarmclock_menu
sudo systemctl restart alarmclock_radio


sudo systemctl stop alarmclock_oled
sudo systemctl stop alarmclock_menu
sudo systemctl stop alarmclock_radio


# debian 12 !
pip3 install --upgrade adafruit-python-shell click
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/raspi-spi-reassign.py
python3 raspi-spi-reassign.py --ce0=5 --ce1=6




