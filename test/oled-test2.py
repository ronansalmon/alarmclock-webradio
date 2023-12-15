import time
import board
import digitalio
import adafruit_ssd1306
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Setting some variables for our reset pin etc.
RESET_PIN = digitalio.DigitalInOut(board.D4)

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c, reset=RESET_PIN)

# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306

oled.fill(0)
oled.show()

fonttime = ImageFont.truetype("DejaVuSerif-Bold", 38)
fontother = ImageFont.truetype("DejaVuSerif",10) 

image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
now = datetime.now()
draw.text((5, 0), now.strftime("%H:%M"),  font=fonttime, fill=255)
draw.text((0, 40), 'spoonradio',  font=fontother, fill=255) 
draw.text((70, 54), now.strftime("%d/%m/%Y"),  font=fontother, fill=255) 
draw.text((00, 54), "07:00",  font=fontother, fill=255) 
oled.image(image)
oled.show()

imageTime = Image.new('1', (oled.width, 38))
draw = ImageDraw.Draw(image)
now = datetime.now()
draw.text((5, 0), now.strftime("%H:%M"),  font=fonttime, fill=255)
draw.text((0, 40), 'spoonradio',  font=fontother, fill=255) 
draw.text((70, 54), now.strftime("%d/%m/%Y"),  font=fontother, fill=255) 
draw.text((00, 54), "07:00",  font=fontother, fill=255) 
oled.image(image)
oled.show()

