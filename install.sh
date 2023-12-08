
sudo usermod -a -G spi,gpio,i2c pi
sudo apt update
sudo apt install -y python3-pip ttf-mscorefonts-installer mosquitto mosquitto-clients python3-virtualenv \
  ffmpeg alsa-utils

virtualenv python
source ~/python/bin/activate

git clone https://github.com/ronansalmon/alarmclock-webradio
cd alarmclock-webradio

pip install -r requirements.txt

sudo ln -sf /home/pi/alarmclock-webradio/alarmclock_radio.service /lib/systemd/system/alarmclock_radio.service
sudo ln -sf /home/pi/alarmclock-webradio/alarmclock_rotary.service /lib/systemd/system/alarmclock_rotary.service
sudo systemctl daemon-reload
sudo systemctl start alarmclock_radio
sudo systemctl start alarmclock_rotary
sudo systemctl enable alarmclock_radio
sudo systemctl enable alarmclock_rotary


sudo systemctl stop dbus
sudo systemctl disable dbus
sudo systemctl stop dbus.socket
sudo systemctl disable dbus.socket
sudo systemctl stop triggerhappy.socket
sudo systemctl disable triggerhappy.socket
sudo systemctl stop triggerhappy
sudo systemctl disable triggerhappy
