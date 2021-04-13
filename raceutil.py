from mkw_ghosts import MkwGhosts
import base64
import binascii
import io

controller_id_dict = {'Controllers.wii_remote':1, 'Controllers.wii_wheel':0, 'Controllers.gamecube_controller':2, 'Controllers.classic_controller':3}

def create_base64_encode(ghostdata, country):
    kaitai = MkwGhosts.from_bytes(ghostdata)
    miidata = bytearray()
    mii = bytes(kaitai.driver_mii_data)
    miidata += mii
    crc_16 = (kaitai.crc16_mii).to_bytes(2, 'big') #leaving out the to_bytes() function will make mkw crash
    miidata += crc_16
    controllerdata = controller_id_dict.get(str(kaitai.controller_id), 3)
    miidata += controllerdata.to_bytes(1, "big")
    unknown = chr(0)
    miidata += bytes(unknown, 'utf8')
    region = (kaitai.region_code).to_bytes(1, 'big')
    miidata += region
    location = bytes([country])
    miidata += location
    encode = base64.b64encode(bytearray(miidata))
    return encode

def channel_time_parse(time):
    minutes = int(time[0:1]) * 60000
    seconds = int(time[2:4]) * 1000
    milliseconds = int(time[5:]) 

    total = minutes + seconds + milliseconds
    return total


