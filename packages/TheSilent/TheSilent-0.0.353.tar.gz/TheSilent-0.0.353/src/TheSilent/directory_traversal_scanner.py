import time
import urllib.parse
import requests
from TheSilent.clear import clear
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RED = "\033[1;31m"

# create html sessions object
web_session = requests.Session()

tor_proxy = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}

# increased security
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

# increased security
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

except AttributeError:
    pass

# scans for directory traversal
def directory_traversal_scanner(url, secure=True, tor=False, delay=1):
    clear()

    my_list = []
    mal_payloads = ["cgi-bin", ".env", ".git", ".../"]

    if url.startswith("https://") or url.startswith("http://"):
        if url.count("/") == 2:
            if url.endswith("/"):
                my_url = url

            else:
                my_url = url + "/"

        else:
            my_url = url

    else:
        if secure:
            if url.count("/") == 0:
                if url.endswith("/"):
                    my_url = "https://" + url

                else:
                    my_url = "https://" + url + "/"

            else:
                my_url = "https://" + url

        else:
            if url.count("/") == 0:
                if url.endswith("/"):
                    my_url = "http://" + url

                else:
                    my_url = "http://" + url + "/"

            else:
                my_url = "http://" + url

    for mal in mal_payloads:
        time.sleep(delay)
        new_url = my_url + urllib.parse.quote(mal)
        print(CYAN + f"checking: {new_url}")
        try:
            if tor:
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).status_code

            else:
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).status_code

            if my_request == 200:
                print(RED + f"True: {new_url}")
                my_list.append(new_url)

            else:
                print(GREEN + f"False: {new_url}")

        except:
            continue

    print(CYAN + "")
    clear()

    return my_list
