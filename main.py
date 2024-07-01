import sys
import os
import neopixel # Imports the neopixel module, which is used to control WS2812 RGB LEDs
from machine import Pin, PWM
import utime

# Append the absolute path to your module
sys.path.append(r'C:\Users\len\MicroPython\RFID_test')

# Print sys.path to verify the path is added correctly
#print("Current sys.path:", sys.path)
print("Program Running")

try:
    from mfrc522 import MFRC522
except ImportError as e:
    print("Error importing MFRC522:", e)
    print("Make sure mfrc522.py is in the directory: C:\\Users\\len\\MicroPython\\RFID_test")
    sys.exit(1)

# Initialize the buzzer, LED, and servo pins
led_pin = Pin(29)
np = neopixel.NeoPixel(led_pin, 1)  # 1 indicates the number of LEDs
buzzer = Pin(17, Pin.OUT)  # Change the pin number according to your setup
servo_pin = Pin(18)  # Change to the pin connected to your servo

# Initialize the servo PWM object
servo = PWM(servo_pin, freq=50)
servo.duty_u16(0)  # Start with the servo at 0 degrees

# Initialize a variable to track servo direction state
servo_direction = 0  # 0 means first direction (0 to 180), 1 means opposite direction (180 to 0)

def green_led():
    np[0] = (57, 255, 20)
    np.write()
    
def white_led():
    np[0] = (1, 1, 1)
    np.write()

def red_led():
    np[0] = (255, 0, 0)
    np.write()
    
def off_led():
    np[0] = (0, 0, 0)
    np.write()

# Function to control the servo and LEDs for access passed
def access_passed():
    global servo_direction  # Declare servo_direction as global
    buzzer.on()
    green_led()
    utime.sleep_ms(300)
    buzzer.off()
    off_led()
    utime.sleep_ms(100)
    
    print("Servo Activated")
    
    if servo_direction == 0:
        # Rotate the servo from 0 to 180 degrees
        for angle in range(0, 180, 5):
            servo.duty_u16(int(1000 + (angle / 180 * 9000)))
            utime.sleep_ms(100)
        servo_direction = 1  # Set direction to opposite for next access
    else:
        # Rotate the servo from 180 to 0 degrees
        for angle in range(180, -5, -5):
            servo.duty_u16(int(1000 + (angle / 160 * 9000)))
            utime.sleep_ms(100)
            # Move back to 0 degrees
            servo.duty_u16(int(1000 + (0 / 180 * 9000)))
            utime.sleep_ms(100)
        servo_direction = 0  # Set direction back to original for next access

        
        
    off_led()  # Turn off green LED after servo movement


# Function to control the LEDs for access denied
def access_denied():
    for _ in range(2):
        buzzer.on()
        red_led()
        utime.sleep_ms(300)
        buzzer.off()
        off_led()
        utime.sleep_ms(100)

# Initialize the MFRC522 reader
reader = MFRC522(spi_id=0, sck=2, miso=4, mosi=3, cs=1, rst=0)

off_led()

print("")
print("Place card into reader")
print("")

# Define the authorized UID
authorized_uid = [0x34, 0x43, 0x5E, 0xA7]

PreviousCard = [0]

try:
    while True:
        reader.init()
        (stat, tag_type) = reader.request(reader.REQIDL)
        if stat == reader.OK:
            (stat, uid) = reader.SelectTagSN()
            if uid == PreviousCard:
                continue

            if stat == reader.OK:
                scan_time = utime.localtime()
                formatted_time = "{:02}:{:02}:{:02}".format(scan_time[3], scan_time[4], scan_time[5])
                print("Card detected at {}\n{}\nuid={}".format(formatted_time, hex(int.from_bytes(bytes(uid), "little", False)).upper(), reader.tohexstring(uid)))
                if uid == authorized_uid:
                    print("Access Passed")
                    access_passed()
                else:
                    print("Access Denied")
                    access_denied()
                print("Done\n")
                PreviousCard = uid
            else:
                PreviousCard = [0]
        utime.sleep_ms(5)

except KeyboardInterrupt:
    print("Program Stop")

