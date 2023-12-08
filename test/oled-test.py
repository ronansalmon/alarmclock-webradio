import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import subprocess
from datetime import datetime


disp = Adafruit_SSD1306.SSD1306_128_32(rst=None)
disp.begin()
# Clear display.
disp.clear()
disp.set_contrast(1)
disp.display()

width = disp.width
height = disp.height


# Draw a black filled box to clear the image.
#draw.rectangle((0,0,width,height), outline=0, fill=0)


fonttime = ImageFont.truetype("DejaVuSerif-Bold",24)
fontalarme = ImageFont.truetype("DejaVuSerif",8) 
fontdate = ImageFont.truetype("DejaVuSerif",8) 

image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
now = datetime.now()
draw.text((0, 5), now.strftime("%H:%M"),  font=fonttime, fill=255)
draw.text((80, 0), now.strftime("%d/%m/%Y"),  font=fontdate, fill=255) 
draw.text((90, 22), "07:00",  font=fontalarme, fill=255) 

disp.image(image)
disp.display()

time.sleep(.1)

