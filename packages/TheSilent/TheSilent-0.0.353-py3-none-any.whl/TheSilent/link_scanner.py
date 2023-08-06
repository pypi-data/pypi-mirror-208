import hashlib
import re
import sys
import time
import requests
from TheSilent.clear import clear
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
RED = "\033[1;31m"

tor_proxy = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}

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


def link_scanner(url, secure=True, tor=False, delay=1):
    clear()

    if secure:
        my_secure = "https://"

    else:
        my_secure = "http://"

    hash_list = []
    website_list = []
    visited_list = []

    website_list.append(my_secure + url)
    tracker = -1

    while True:
        time.sleep(delay)
        
        length_count = 0
        tracker += 1
        website_list = list(set(website_list))

        # checks whether a url is valid
        valid_url_count = -1

        while True:
            try:
                valid_url_count += 1
                for i in website_list[valid_url_count].lower():
                    valid_regex = re.search("[\d\w\-\?\.=:/&]", i)

                    if not valid_regex or "script" in website_list[valid_url_count]:
                        website_list.pop(valid_url_count)
                        valid_url_count -= 1
                        break

            except IndexError:
                break

        # start checking for urls
        visited = False
        for visits in visited_list:
            try:
                if visits == website_list[tracker]:
                    visited = True

            except IndexError:
                break

        if not visited:
            try:
                if tor:
                    stream_boolean = web_session.get(website_list[tracker], verify=False, headers=user_agent, proxies=tor_proxy, timeout=(60,120), stream=True)

                    for i in stream_boolean.iter_lines():
                        length_count += len(i)

                else:
                    stream_boolean = web_session.get(website_list[tracker], verify=False, headers=user_agent, timeout=(5,30), stream=True)

                    for i in stream_boolean.iter_lines():
                        length_count += len(i)

            except IndexError:
                break

            except:
                print(RED + "ERROR! " + website_list[tracker])
                website_list.pop(tracker)
                tracker -= 1
                continue

            if length_count <= 100000000:
                try:
                    print(CYAN + website_list[tracker])

                    if tor:
                        my_request = web_session.get(website_list[tracker], verify=False, headers=user_agent, proxies=tor_proxy, timeout=(60,120)).text

                    else:
                        my_request = web_session.get(website_list[tracker], verify=False, headers=user_agent, timeout=(5,30)).text

                    page_hash = hashlib.sha3_512(my_request.encode("utf8")).hexdigest()

                    already_visited = False

                    for hashes in hash_list:
                        if hashes == page_hash:
                            already_visited = True
                            visited_list.append(website_list[tracker])
                            website_list.pop(tracker)
                            tracker -= 1
                            break

                    if already_visited == False:
                        visited_list.append(website_list[tracker])
                        
                        hash_list.append(page_hash)

                        http_url = re.findall("http://\S+|https://", my_request)
                        for links in http_url:
                            if url in links:
                                website_list.append(links)

                        javascript_url = re.findall("[\"\'](/\S+)[\"\']", my_request)
                        for links in javascript_url:
                            if url in links:
                                website_list.append(links)

                        href_url = re.findall("href=[\"\'](\S+)[\"\']", my_request)
                        for links in href_url:
                            if "http://" in links or "https://" in links:
                                if url in links:
                                    website_list.append(links)

                            elif links.startswith("/"):
                                website_list.append(my_secure + url + links)

                            else:
                                website_list.append(my_secure + url + "/" + links)

                        src_url = re.findall("src=[\"\'](\S+)[\"\']", my_request)
                        for links in src_url:
                            if "http://" in links or "https://" in links:
                                if url in links:
                                    website_list.append(links)

                            elif links.startswith("/"):
                                website_list.append(my_secure + url + links)

                            else:
                                website_list.append(my_secure + url + "/" + links)

                except:
                    continue

    website_list = list(set(website_list[:]))
    print(CYAN + "")
    clear()
    return website_list
