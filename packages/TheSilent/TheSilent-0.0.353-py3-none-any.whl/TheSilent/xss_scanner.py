import re
import time
import urllib.parse
import requests
from TheSilent.clear import clear
from TheSilent.form_scanner import form_scanner
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

# scans for xss
def xss_scanner(url, secure=True, tor=False, delay=1):
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
                
    # define payloads
    init_mal_payloads = ["<div>the silent</div>", "<em>the silent</em>", "<iframe>the silent</iframe>", "<input type='text' id='thesilent' name='thesilent' value='thesilent'>", "<p>the silent</p>", "<script>alert('the silent')</script>", "<script>prompt('the silent')</script>", "<strong>the silent</strong>"]

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
        
    mal_scripts = [
        "<div>the silent</div>",
        "<DIV>THE SILENT</DIV>",
        "<em>the silent</em>",
        "<EM>THE SILENT</EM>",
        "<iframe>the silent</iframe>",
        "<IFRAME>THE SILENT</IFRAME>",
        "<input type='text' id='thesilent' name='thesilent' value='thesilent'>",
        "<INPUT TYPE='TEXT' ID='THESILENT' NAME='THESILENT' VALUE='THESILENT'>",
        "<p>the silent</p>",
        "<P>THE SILENT</P>",
        "<script>alert('the silent')</script>",
        "<SCRIPT>ALERT('THE SILENT')</SCRIPT>",
        "<script>prompt('the silent')</script>",
        "<SCRIPT>PROMPT('THE SILENT')</SCRIPT>",
        "<strong>the silent</strong>",
        "<STRONG>THE SILENT</STRONG>"]

    my_list = []

    # check for xss in url
    for mal in url_mal_payloads:
        time.sleep(delay)
        new_url = my_url + urllib.parse.quote(mal)
        print(CYAN + f"checking: {new_url}")
        try:
            if tor:
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text

            else:
                my_request = web_session.get(new_url, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text

            alert = False
            for script in mal_scripts:
                if script in my_request:
                    print(RED + f"True: {new_url}")
                    my_list.append(new_url)
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False: {new_url}")

        except:
            continue

    # check for xss in headers
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + f"checking headers: {my_url} {mal}:{mal}")
        try:
            if tor:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, proxies=tor_proxy, timeout=(60,120)).text

            else:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, timeout=(5,30)).text

            alert = False
            for script in mal_scripts:
                if script in my_request:
                    print(RED + f"True headers: {my_url} {mal}:{mal}")
                    my_list.append(f"headers: {my_url} {mal}:{mal}")
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False headers: {my_url} {mal}:{mal}")

        except:
            continue

    # check for xss in cookies
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + f"checking cookie: {my_url} {mal}:{mal}")
        try:
            if tor:
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text

            else:
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text

            alert = False
            for script in mal_scripts:
                if script in my_request:
                    print(RED + f"True cookies: {my_url} {mal}:{mal}")
                    my_list.append(f"cookies: {my_url} {mal}:{mal}")
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False cookies: {my_url} {mal}:{mal}")

        except:
            continue

    # check for xss in forms
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
                            
                            print(CYAN + f"checking: forms: {new_url} {name}:{mal}")
                            if method == "get":
                                if tor:
                                    my_request = web_session.get(new_url, params={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text

                                else:
                                    my_request = web_session.get(new_url, params={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text
                                        
                            if method == "post":
                                if tor:
                                    my_request = web_session.post(new_url, data={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text

                                else:
                                    my_request = web_session.post(new_url, data={name:mal}, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text

                alert = False
                for script in mal_scripts:
                    if script in my_request:
                        print(RED + f"True forms: {new_url} {name}:{mal}")
                        my_list.append(f"forms: {new_url} {name}:{mal}")
                        alert = True
                        break

                if not alert:
                    print(GREEN + f"False forms: {new_url} {name}:{mal}")

            except:
                continue

    print(CYAN + "")
    clear()

    my_list.sort()

    return my_list
