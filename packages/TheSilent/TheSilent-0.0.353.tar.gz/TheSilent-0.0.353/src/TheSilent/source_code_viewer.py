from TheSilent.clear import clear

CYAN = "\033[1;36m"

# attempts to view source code of file
def source_code_viewer(file, keyword=""):
    clear()

    count = 0

    with open(file, "rb") as f:
        for i in f:
            result = i.decode(errors="ignore")
            if keyword in result:
                print(CYAN + result)
                count += 1

                if count == 128:
                    count = 0
                    pause = input()

    print(CYAN + "\ndone")
