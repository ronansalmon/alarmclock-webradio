
sudo usermod -a -G spi,gpio,i2c pi
sudo apt update
sudo apt install -y python3-pip ttf-mscorefonts-installer mosquitto mosquitto-clients python3-virtualenv \
  ffmpeg alsa-utils

cd /app
virtualenv python
source /app/python/bin/activate

git clone https://github.com/ronansalmon/alarmclock-webradio
cd alarmclock-webradio

pip install -r requirements.txt

#sudo ln -sf /app/alarmclock-webradio/alarmclock_oled_i2c.service /lib/systemd/system/alarmclock_oled.service
sudo ln -sf /app/alarmclock-webradio/alarmclock_oled_spi.service /lib/systemd/system/alarmclock_oled.service
sudo ln -sf /app/alarmclock-webradio/alarmclock_menu.service /lib/systemd/system/alarmclock_menu.service
sudo ln -sf /app/alarmclock-webradio/alarmclock_radio.service /lib/systemd/system/alarmclock_radio.service
sudo systemctl daemon-reload
sudo systemctl enable --now systemd-time-wait-sync.service
sudo systemctl start alarmclock_oled
sudo systemctl start alarmclock_menu
sudo systemctl start alarmclock_radio
sudo systemctl enable alarmclock_oled
sudo systemctl enable alarmclock_menu
sudo systemctl enable alarmclock_radio

sudo systemctl stop dbus
sudo systemctl disable dbus
sudo systemctl stop dbus.socket
sudo systemctl disable dbus.socket
sudo systemctl stop triggerhappy.socket
sudo systemctl disable triggerhappy.socket
sudo systemctl stop triggerhappy
sudo systemctl disable triggerhappy
sudo systemctl disable sshswitch.service


