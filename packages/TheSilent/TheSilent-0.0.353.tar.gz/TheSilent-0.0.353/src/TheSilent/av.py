import os
from TheSilent.clear import clear

CYAN = "\033[1;36m"
RED = "\033[1;31m"


def av(my_dir):
    malware_strings = ["GetWindowsDirectoryW", "EncryptFiles", "EncryptFileSystem", "EncryptFileW", "extensionsToEncrypt", "ImpersonateLoggedOnUser", "IsDebuggerPresent", "RegCloseKey", "RegCreateKey", "RegDeleteKey", "RegEnumKey", "RegFlushKey", "RegLoadKey", "RegOpenKey", "RegQueryInfoKey", "RegQueryValue", "RegSetValue", "TerminateProcess"]

    malware_list = []

    clear()

    for path, directories, files in os.walk(my_dir):
        for file in files:
            scan = path + "/" + file
            
            malware_hits = 0

            try:
                if os.stat(scan).st_size > 0 and os.stat(scan).st_size < 1000000000:
                    print(CYAN + "checking: " + scan)
                    with open(scan, "rb") as f:
                        # scan for known malware strings
                        f.seek(0)
                        detected_strings = []
                        skip = False
                        for i in f:
                            result = i.decode(errors="replace")
                            for mal in malware_strings:
                                for detect in detected_strings:
                                    if detect == mal:
                                        skip = True
                                        
                                if mal in result and malware_hits < len(malware_strings) and not skip:
                                    malware_hits += 1
                                    detected_strings.append(mal)

                if malware_hits > 0:
                    chance = 100 * (malware_hits / len(malware_strings))
                    if chance > 50:
                        print(RED + f"{chance}% malware: " + scan)
                        malware_list.append(f"{chance}% malware: " + scan)

            except PermissionError:
                print(RED + "ERROR! Permission error!")
                continue

            except:
                continue

    clear()

    malware_list = list(set(malware_list))
    malware_list.sort()

    if len(malware_list) > 0:
        for malware in malware_list:
            print(RED + malware)

        print(RED + f"\n{len(malware_list)} possible threats detected!")

    else:
        print(CYAN + "No threats detected!")
