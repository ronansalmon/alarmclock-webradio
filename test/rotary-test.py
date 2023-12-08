from pyky040 import pyky040
import threading

# Define your callback
def my_callback(scale_position):
    print('Hello world! The scale position is {}'.format(scale_position))

def dec_callback_volume(scale_position):
    print('Hello volume! dec_callback The scale position is {}'.format(scale_position))

def inc_callback_volume(scale_position):
    print('Hello volume! inc_callback The scale position is {}'.format(scale_position))

def click_volume():
    print('Hello volume! click is')
    
def dec_callback_menu(scale_position):
    print('Hello menu! dec_callback The scale position is {}'.format(scale_position))

def inc_callback_menu(scale_position):
    print('Hello menu! inc_callback The scale position is {}'.format(scale_position))

def click_menu():
    print('Hello menu! click is')

rotary_volume = pyky040.Encoder(CLK=13, DT=6, SW=5)
rotary_volume.setup(scale_min=0, scale_max=100, step=1, sw_callback=click_volume, inc_callback=inc_callback_volume, dec_callback=dec_callback_volume)

rotary_menu = pyky040.Encoder(CLK=22, DT=27, SW=17)
rotary_menu.setup(scale_min=0, scale_max=100, step=1, sw_callback=click_menu, inc_callback=inc_callback_menu, dec_callback=dec_callback_menu)


thread_volume = threading.Thread(target=rotary_volume.watch)
thread_menu = threading.Thread(target=rotary_menu.watch)

# Launch the thread
thread_volume.start()
thread_menu.start()
