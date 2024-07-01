from mfrc522 import MFRC522
from rfidaccess import RfidAccess
import utime

reader = MFRC522(spi_id=0, sck=2, miso=4, mosi=3, cs=1, rst=0)
access = RfidAccess()

print("")
print("Please place card on reader")
print("")

def checksum(data):
    crc = 0xc7
    for byte in data:
        crc ^= byte
        for _ in range(8):
            msb = crc & 0x80
            crc = (crc << 1) & 0xff
            if msb:
                crc ^= 0x1d
    return crc

def create_ndef_message(url):
    prefix_mapping = {
        "http://www.": 0x01,
        "https://www.": 0x02,
        "http://": 0x03,
        "https://": 0x04
    }
    prefix = None
    for key in prefix_mapping:
        if url.startswith(key):
            prefix = key
            break
    if prefix:
        prefix_byte = prefix_mapping[prefix]
        url_no_prefix = url[len(prefix):]
    else:
        prefix_byte = 0x00
        url_no_prefix = url
    ndef_message = [
        0xd1, 0x01, len(url_no_prefix) + 1, 0x55, prefix_byte
    ]
    ndef_message.extend(ord(char) for char in url_no_prefix)
    return ndef_message

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
                defaultKey = [255, 255, 255, 255, 255, 255]
                firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
                nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]

                # Set MAD sector
                access.setTrailerAccess(keyA_Write=access.KEYB, access_Read=access.KEYAB, access_Write=access.KEYB,
                                        keyB_Read=access.NEVER, keyB_Write=access.KEYB)
                access.setBlockAccess(access.ALLBLOCK, access_Read=access.KEYAB, access_Write=access.KEYB,
                                      access_Inc=access.NEVER, access_Dec=access.NEVER)
                block3 = access.fillBlock3(keyA=firstSectorKey, keyB=defaultKey)
                if reader.writeSectorBlock(uid, 0, 3, block3, keyA=defaultKey) == reader.ERR:
                    print("Writing MAD sector failed!")
                else:
                    print(".", end="")
                    b1 = [0x14, 0x01, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1]
                    b1[0] = checksum(b1[1:])  # I know this is already ok but just to demonstrate the CRC
                    reader.writeSectorBlock(uid, 0, 1, b1, keyB=defaultKey)
                    b2 = [0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1, 0x03, 0xE1]
                    reader.writeSectorBlock(uid, 0, 2, b1, keyB=defaultKey)
                    access.setTrailerAccess(keyA_Write=access.KEYB, access_Read=access.KEYAB, access_Write=access.KEYB,
                                            keyB_Read=access.NEVER, keyB_Write=access.KEYB)
                    access.setBlockAccess(access.ALLBLOCK, access_Read=access.KEYAB, access_Write=access.KEYAB,
                                          access_Inc=access.KEYAB, access_Dec=access.KEYAB)
                    block3 = access.fillBlock3(keyA=nextSectorKey, keyB=defaultKey)
                    for sector in range(1, 16):
                        if reader.writeSectorBlock(uid, sector, 3, block3, keyA=defaultKey) == reader.ERR:
                            print("\nWriting to sector ", sector, " Failed!")
                            break
                        else:
                            print(".", end="")

                    # Create and write the NDEF message
                    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    ndef_message = create_ndef_message(url)
                    ndef_message.extend([0] * (16 - len(ndef_message)))  # Pad the message to fit into one block
                    reader.writeSectorBlock(uid, 1, 0, ndef_message, keyB=defaultKey)

                    print("\nNDEF message written to the card.")
                    previousCard = uid
                    break
        else:
            PreviousCard = [0]
        utime.sleep_ms(50)

except KeyboardInterrupt:
    print("Bye")
