from machine import Pin, SPI
from mfrc522 import MFRC522
import time

# Define your SPI and pin configuration here
sck = 2     # GPIO2 / Pin 2 for SCK
mosi = 3    # GPIO3 / Pin 3 for MOSI
miso = 4    # GPIO4 / Pin 4 for MISO
cs = 1      # GPIO1 / Pin 1 for CS
rst = 0     # GPIO0 / Pin 0 for RST

# Initialize SPI
spi = SPI(0, baudrate=1000000, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))

# Initialize MFRC522
rfid = MFRC522(spi, sck, mosi, miso, Pin(cs), Pin(rst))

print("Place your Navigo card near the reader...")

while True:
    (stat, tag_type) = rfid.request(rfid.REQIDL)

    if stat == rfid.OK:
        (stat, raw_uid) = rfid.anticoll()

        if stat == rfid.OK:
            print("UID: %s" % ":".join([hex(i) for i in raw_uid]))

            # Uncomment the following lines to select and read specific data blocks
            # if rfid.select_tag(raw_uid) == rfid.OK:
            #     for block_num in range(0, 64):
            #         (stat, block) = rfid.read(block_num)
            #         if stat == rfid.OK:
            #             print("Block %d: %s" % (block_num, block))
            #         else:
            #             print("Failed to read block %d" % block_num)

    time.sleep(1)
