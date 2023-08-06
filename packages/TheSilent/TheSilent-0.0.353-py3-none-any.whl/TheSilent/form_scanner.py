import re
import requests
from TheSilent.return_user_agent import return_user_agent

# create html sessions object
web_session = requests.Session()

# fake user agent
user_agent = {"User-Agent": return_user_agent()}

tor_proxy = {
    "https": "socks5h://localhost:9050",
    "http": "socks5h://localhost:9050"}

# increased security
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

# increased security
try:
    requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ":HIGH:!DH:!aNULL"

except AttributeError:
    pass

# scans for forms


def form_scanner(url, secure=True, tor=False, parse="forms"):
    if "https://" not in url and "http://" not in url:
        if secure:
            my_secure = "https://"

        else:
            my_secure = "http://"

        url = my_secure + url

    try:
        if tor:
            result = web_session.get(url, verify=False, headers=user_agent, proxies=tor_proxy, timeout=(60,120)).text

        else:
            result = web_session.get(url, verify=False, headers=user_agent, timeout=(5,30)).text

        try:
            if parse == "forms":
                forms = re.findall("<form[\n\\w\\S\\s]+?form>", result)
                return forms

            if parse == "input":
                input_form = re.findall("<input.+?>", result)
                return input_form

        except UnicodeDecodeError:
            return []

    except:
        return []
