from TheSilent.clear import clear
from TheSilent.command_injection_scanner import command_injection_scanner
from TheSilent.directory_traversal_scanner import directory_traversal_scanner
from TheSilent.python_injection_scanner import python_injection_scanner
from TheSilent.sql_injection_scanner import sql_injection_scanner
from TheSilent.xss_scanner import xss_scanner

CYAN = "\033[1;36m"

# scans for security flaws and bad practices
def web_scanner(url, secure=True, tor=False, delay=1, report=True):
    clear()

    my_directory_traversal_scanner = directory_traversal_scanner(url=url, secure=secure, tor=tor, delay=delay)
    my_command_injection_scanner = command_injection_scanner(url=url, secure=secure, tor=tor, delay=delay)
    my_python_injection_scanner = python_injection_scanner(url=url, secure=secure, tor=tor, delay=delay)
    my_sql_injection_scanner = sql_injection_scanner(url=url, secure=secure, tor=tor, delay=delay)
    my_xss_scanner = xss_scanner(url=url, secure=secure, tor=tor, delay=delay)

    clear()

    print(CYAN + "command injection:")
    for i in my_command_injection_scanner:
        if report:
            if "http://" in url:
                with open(url[7:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                    
            if "https://" in url:
                with open(url[8:] +  ".txt", "a") as f:
                    f.write(i + "\n")

        print(CYAN + i)

    print(CYAN + "")
    print(CYAN + "directory traversal:")
    for i in my_directory_traversal_scanner:
        if report:
            if "http://" in url:
                with open(url[7:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                    
            if "https://" in url:
                with open(url[8:] +  ".txt", "a") as f:
                    f.write(i + "\n")

        print(CYAN + i)

    print(CYAN + "")
    print(CYAN + "python injection:")
    for i in my_python_injection_scanner:
        if report:
            if "http://" in url:
                with open(url[7:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                    
            if "https://" in url:
                with open(url[8:] +  ".txt", "a") as f:
                    f.write(i + "\n")

        print(CYAN + i)

    print(CYAN + "")
    print(CYAN + "sql injection:")
    for i in my_sql_injection_scanner:
        if report:
            if "http://" in url:
                with open(url[7:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                    
            if "https://" in url:
                with open(url[8:] +  ".txt", "a") as f:
                    f.write(i + "\n")

        print(CYAN + i)

    print(CYAN + "")
    print(CYAN + "xss:")
    for i in my_xss_scanner:
        if report:
            if "http://" in url:
                with open(url[7:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                    
            if "https://" in url:
                with open(url[8:] +  ".txt", "a") as f:
                    f.write(i + "\n")
                
        print(CYAN + i)
