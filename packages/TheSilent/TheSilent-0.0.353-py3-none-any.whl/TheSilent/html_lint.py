import re
import time
import requests
from TheSilent.clear import clear
from TheSilent.link_scanner import link_scanner
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
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

def html_lint(url, secure=True, crawl="0", delay=1, tor=False, parse="", problem="all", report=True):
    clear()

    linted = []
    
    crawler = link_scanner(url, secure=secure, crawl=crawl, delay=delay, tor=tor, parse=parse)

    for crawl in crawler:
        print(CYAN + "checking: " + crawl)
        # prevent dos attacks
        time.sleep(delay)

        try:
            if tor:
                result = web_session.get(crawl, verify=False, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text.lower()

            else:
                result = web_session.get(crawl, verify=False, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text.lower()

            area_tag = re.findall("<area.+>", result)

            for area in area_tag:
                if "alt" not in area:
                    print(RED + f"no alt in area tag detected on {crawl}. Consider using alt (accessibility).")
                    linted.append(f"no alt in area tag detected on {crawl}. Consider using alt (accessibility).")

            image_tag = re.findall("<img.+>", result)

            for image in image_tag:
                if "alt" not in image:
                    print(RED + f"no alt in img tag detected on {crawl}. Consider using alt (accessibility).")
                    linted.append(f"no alt in img tag detected on {crawl}. Consider using alt (accessibility).")

            input_tag = re.findall("<input.+>", result)

            for my_input in input_tag:
                if "alt" not in my_input and "image" in my_input:
                    print(RED + f"no alt in input image tag detected on {crawl}. Consider using alt (accessibility).")
                    linted.append(f"no alt in input image tag detected on {crawl}. Consider using alt (accessibility).")

            if "<b>" in result:
                print(RED + f"<b> detected on {crawl}. Consider using <strong> (accessibility).")
                linted.append(f"<b> detected on {crawl}. Consider using <strong> (accessibility).")

            if "document.write" in result:
                print(RED + f"document.write detected on {crawl}. This has weird behavior (behavior).")
                linted.append(f"document.write detected on {crawl}. This has weird behavior (behavior).")

            if "<i>" in result:
                print(RED + f"<i> detected on {crawl}. Consider using <em> (accessibility).")
                linted.append(f"<i> detected on {crawl}. Consider using <em> (accessibility).")

            if "innerhtml" in result:
                print(RED + f"innerhtml detected on {crawl}. This could lead to a security vulnerability (security).")
                linted.append(f"innerhtml detected on {crawl}. This could lead to a security vulnerability (security).")

        except:
            continue

    linted = list(set(linted))
    linted.sort()

    clear()

    no_problems = True

    for lint in linted:
        if problem == "all":
            if report:
                with open(url + ".txt", "a") as f:
                    f.write(lint + "\n")
                    
            print(RED + lint)
            no_problems = False

        if problem == "access" and "accessibility" in lint:
            if report:
                with open(url + ".txt", "a") as f:
                    f.write(lint + "\n")
                    
            print(RED + lint)
            no_problems = False

        if problem == "behavior" and "behavior" in lint:
            if report:
                with open(url + ".txt", "a") as f:
                    f.write(lint + "\n")
                    
            print(RED + lint)
            no_problems = False

        if problem == "security" and "security" in lint:
            if report:
                with open(url + ".txt", "a") as f:
                    f.write(lint + "\n")
                    
            print(RED + lint)
            no_problems = False

    if no_problems:
        if report:
                with open(url + ".txt", "a") as f:
                    f.write("No problems deteced!")
                    
        print(CYAN + "No problems deteced!")
