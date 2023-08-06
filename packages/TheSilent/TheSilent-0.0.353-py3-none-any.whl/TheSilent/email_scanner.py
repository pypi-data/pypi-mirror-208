import re
import requests
from TheSilent.clear import clear
from TheSilent.link_scanner import link_scanner
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
RED = "\033[1;31m"

tor_proxy = {"http": "socks5h://localhost:9050",
             "https": "socks5h://localhost:9050"}

# create html sessions object
web_session = requests.Session()

# fake user agent
user_agent = {"User-Agent": return_user_agent()}

# increased security
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

# increased security
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

except AttributeError:
    pass

# scans for emails on a website


def email_scanner(url, secure=True, tor=False, crawl="all", parse=" "):
    if secure:
        my_secure = "https://"

    else:
        my_secure = "http://"

    my_url = my_secure + url
    email_list = []
    website_list = []
    website_list.append(my_url)

    clear()
    links = link_scanner(url, secure=secure, tor=tor, crawl=crawl, parse=parse)

    for link in links:
        try:
            if tor:
                my_request = web_session.get(link, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60, 120)).text

            else:
                my_request = web_session.get(link, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5, 30)).text

            email = re.findall("[a-z0-9\\.]+@[a-z0-9]+[.][a-z]+", my_request)

            for emails in email:
                email_list.append(emails)

        except BaseException:
            continue

    clear()

    email_list = sorted(set(email_list))

    return email_list
