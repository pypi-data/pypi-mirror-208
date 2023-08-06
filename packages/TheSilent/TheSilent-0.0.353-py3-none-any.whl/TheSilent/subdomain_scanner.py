import re
from TheSilent.link_scanner import link_scanner
from TheSilent.clear import clear

CYAN = "\033[1;36m"

# scans for subdomains
def subdomain_scanner(url, secure=True, tor=False, crawl="all", delay=1, my_file=" "):
    domain_list = []

    website = []

    if my_file == " ":
        website = link_scanner(
            url,
            secure=secure,
            tor=tor,
            crawl=crawl,
            parse=url,
            delay=delay)

    if my_file != " ":
        with open(my_file, "r", errors="ignore") as file:
            for i in file:
                clean = i.replace("\n", "")
                website.append(clean)

    clear()

    for i in website:
        domain = re.findall("(http://|https://)(.+)\\." + url, i)

        try:
            result = domain[0][1]
            domain_list.append(result)

        except:
            continue

    domain_list = list(set(domain_list))

    return domain_list
