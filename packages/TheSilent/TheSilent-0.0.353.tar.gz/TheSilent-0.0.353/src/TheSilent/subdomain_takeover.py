import requests
from TheSilent.subdomain_scanner import subdomain_scanner
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"



# create html sessions object
web_session = requests.Session()

tor_proxy = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050"}

# increased security
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

# increased security
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

except AttributeError:
    pass

# scans for subdomain takeovers
def subdomain_takeover(url, secure=True, tor=False, my_file=" ", parse=" ", crawl="all"):
    result = subdomain_scanner(url, secure=secure, tor=tor, my_file=my_file, parse=parse, crawl=crawl)

    clear()

    vuln_list = []

    if secure:
        my_secure = "https://"

    if secure:
        my_secure = "http://"

    for i in result:
        my_url = my_secure + str(i) + "." + str(url)

        print(CYAN + "checking: " + my_url)

        try:
            if tor:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).status_code

            else:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).status_code

            if my_request == 404:
                print(CYAN + True)
                vuln_list.append(my_url)

            else:
                print(CYAN + "False")

        except:
            print(CYAN + "False")

    clear()

    return vuln_list
