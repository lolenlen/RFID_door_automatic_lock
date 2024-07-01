from machine import Pin, SPI
import mfrc522
import time

# Initialize SPI
sck = Pin(2, Pin.OUT)
mosi = Pin(3, Pin.OUT)
miso = Pin(4)
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

# Initialize the RFID reader with correct pin numbers
rfid = mfrc522.MFRC522(2, 3, 4, 0, 1)  # sck, mosi, miso, rst, cs

print("Place your RFID card near the reader...")

while True:
    rfid.init()
    (status, tag_type) = rfid.request(rfid.REQIDL)
    
    if status == rfid.OK:
        print("Card detected")
        
        (status, uid) = rfid.anticoll(rfid.PICC_ANTICOLL1)
        
        if status == rfid.OK:
            print("UID:", [hex(i) for i in uid])
            
            # Select the scanned tag
            (select_status, selected_uid) = rfid.SelectTag(uid)
            if select_status == rfid.OK:
                print("Tag selected with UID:", [hex(i) for i in selected_uid])
                
                # Read block 8 (or any other block, depending on the card type and your needs)
                status, data = rfid.read(8)
                
                if status == rfid.OK:
                    print("Data on block 8:", data)
                else:
                    print("Failed to read data from block 8")
                    
                # If needed, write data to a block (e.g., block 8)
                # new_data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]
                # status = rfid.write(8, new_data)
                # if status == rfid.OK:
                #     print("Data written to block 8")
                # else:
                #     print("Failed to write data to block 8")
                
                rfid.antenna_on(False)  # Turn off antenna
            else:
                print("Failed to select tag")
        else:
            print("Failed to read UID")
            
    time.sleep(1)
