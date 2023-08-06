import os
from TheSilent.clear import clear

CYAN = "\033[1;36m"
RED = "\033[1;31m"

# securely destroys data


def secure_overwrite(file):
    clear()

    try:
        size = os.path.getsize(file)
        for i in range(1, 8):
            clear()
            print(CYAN + "pass: " + str(i))
            with open(file, "wb") as f:
                for byte in range(size):
                    f.seek(byte)
                    f.write(b"0")

    except PermissionError:
        print(RED + "ERROR! Permission denied!")
        exit()

    except OSError:
        pass

    print(CYAN + file)
    print(CYAN + "done")
