import sys
import os
from machine import Pin, PWM
import utime

# Append the absolute path to your module
sys.path.append(r'C:\Users\len\MicroPython\RFID_test')

# Print sys.path to verify the path is added correctly
print("Current sys.path:", sys.path)

try:
    from mfrc522 import MFRC522
except ImportError as e:
    print("Error importing MFRC522:", e)
    print("Make sure mfrc522.py is in the directory: C:\\Users\\len\\MicroPython\\RFID_test")
    sys.exit(1)

# Initialize the buzzer, LED, and servo pins
buzzer = Pin(15, Pin.OUT)  # Change the pin number according to your setup
green_led = Pin(14, Pin.OUT)  # Pin for the green LED, change as needed
red_led = Pin(13, Pin.OUT)  # Pin for the red LED, change as needed
servo_pin = Pin(12)  # Change to the pin connected to your servo

# Initialize the servo PWM object
servo = PWM(servo_pin, freq=50)
servo.duty_u16(0)  # Start with the servo at 0 degrees

# Function to control the servo and LEDs for access passed
def access_passed():
    buzzer.on()
    green_led.on()
    red_led.off()
    utime.sleep_ms(100)
    buzzer.off()
    green_led.off()
    utime.sleep_ms(100)
    # Rotate the servo from 0 to 180 degrees
    for angle in range(0, 181, 5):
        servo.duty_u16(int(1000 + (angle / 180 * 9000)))  # 1000-10000 range for 0-180 degrees
        utime.sleep_ms(100)
    green_led.off()  # Turn off green LED after servo movement

# Function to control the LEDs for access denied
def access_denied():
    for _ in range(2):
        buzzer.on()
        red_led.on()
        utime.sleep_ms(100)
        buzzer.off()
        red_led.off()
        utime.sleep_ms(100)

# Initialize the MFRC522 reader
reader = MFRC522(spi_id=0, sck=2, miso=4, mosi=3, cs=1, rst=0)

print("")
print("Place card into reader")
print("")

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
                print("Card detected {}  uid={}".format(hex(int.from_bytes(bytes(uid), "little", False)).upper(), reader.tohexstring(uid)))
                firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
                nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]

                # Read MAD sector (first sector)
                if reader.MFRC522_DumpClassic1K(uid, Start=0, End=4, keyA=firstSectorKey) == reader.OK:
                    # Read the rest of the card
                    reader.MFRC522_DumpClassic1K(uid, Start=4, End=64, keyA=nextSectorKey)
                    access_passed()
                    print(" Access Passed")
                else:
                    access_denied()
                    print(" Access Denied")
                print("Done")
                PreviousCard = uid
            else:
                PreviousCard = [0]
        utime.sleep_ms(5)

except KeyboardInterrupt:
    print("Program Stop")
