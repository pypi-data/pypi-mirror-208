import binascii
import random
import os
import socket
import sys
from sys import platform
from TheSilent.clear import clear

CYAN = "\033[1;36m"
RED = "\033[1;31m"

def ap(name, interface):
    clear()

    hex_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    mac = "a4b239"
    for _ in range(6):
        mac += hex_characters[random.randint(0,15)]
        
    name = str(binascii.hexlify(name.encode())).replace("b'", "")
    name = name.replace("'", "")
    name_length = str(hex(int(len(name) / 2)))
    if len(name_length) % 2 == 0:
        name_length = name_length.replace("0x", "")

    else:
       name_length = name_length.replace("x", "")

    try:
        if platform == "linux":
            os.system(f"sudo ip link set {interface} down")
            os.system(f"sudo iw {interface} set monitor control")
            os.system(f"sudo ip link set {interface} up")

            my_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
            my_socket.bind((interface, 0))
            my_code = binascii.unhexlify("000018002e4000a02008000000026c09a000bd000000bd0080000000ffffffffffff" + mac.lower() + mac.lower() + "00019f11770a4f0100006400010400" + name_length + name + "010882848b962430486c0301010504000100002a01002f010032040c121860dd090010180200f02c0000dd180050f2020101800003a4000027a4000042435e0062322f00")

        else:
            print(RED + "Unsupported platform! Linux is required for this tool!")
            sys.exit()
            
    except PermissionError:
        print(RED + "ERROR! Permission Denied!")
        sys.exit()
        

    while True:
        print(CYAN + "*", end="", flush=True)
        try:
            my_socket.sendall(my_code)

        except OSError:
            os.system(f"sudo ip link set {interface} down")
            os.system(f"sudo iw {interface} set monitor control")
            os.system(f"sudo ip link set {interface} up")
