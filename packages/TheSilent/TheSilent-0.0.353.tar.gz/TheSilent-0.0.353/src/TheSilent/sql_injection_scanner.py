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
def sql_injection_scanner(url, secure=True, tor=False, delay=1):
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
    init_mal_payloads = ["'", '"', "*", ";", "`", "')", '")', "*)", ";)", "`)", "'))", '"))', "*))", ";))", "`))", "')))", '")))', "*)))", ";)))", "`)))"]

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

    # sql errors  
    mal_sql = ["SQL syntax.*?MySQL",
        "Warning.*?\\Wmysqli?_",
        "MySQLSyntaxErrorException",
        "valid MySQL result",
        "check the manual that (corresponds to|fits) your MySQL server version",
        "check the manual that (corresponds to|fits) your MariaDB server version",
        "check the manual that (corresponds to|fits) your Drizzle server version",
        "Unknown column '[^ ]+' in 'field list'",
        "MySqlClient\\.",
        "com\\.mysql\\.jdbc",
        "Zend_Db_(Adapter|Statement)_Mysqli_Exception",
        "Pdo\\[./_\\]Mysql",
        "MySqlException",
        "SQLSTATE\\[\\d+\\]: Syntax error or access violation",
        "MemSQL does not support this type of query",
        "is not supported by MemSQL",
        "unsupported nested scalar subselect",
        "PostgreSQL.*?ERROR",
        "Warning.*?\\Wpg_",
        "valid PostgreSQL result",
        "Npgsql\\.",
        "PG::SyntaxError:",
        "org\\.postgresql\\.util\\.PSQLException",
        "ERROR:\\s\\ssyntax error at or near",
        "ERROR: parser: parse error at or near",
        "PostgreSQL query failed",
        "org\\.postgresql\\.jdbc",
        "Pdo\\[./_\\]Pgsql",
        "PSQLException",
        "OLE DB.*? SQL Server",
        "\bSQL Server[^&lt;&quot;]+Driver",
        "Warning.*?\\W(mssql|sqlsrv)_",
        "\bSQL Server[^&lt;&quot;]+[0-9a-fA-F]{8}",
        "System\\.Data\\.SqlClient\\.(SqlException|SqlConnection\\.OnError)",
        "(?s)Exception.*?\bRoadhouse\\.Cms\\.",
        "Microsoft SQL Native Client error '[0-9a-fA-F]{8}",
        "\\[SQL Server\\]",
        "ODBC SQL Server Driver",
        "ODBC Driver \\d+ for SQL Server",
        "SQLServer JDBC Driver",
        "com\\.jnetdirect\\.jsql",
        "macromedia\\.jdbc\\.sqlserver",
        "Zend_Db_(Adapter|Statement)_Sqlsrv_Exception",
        "com\\.microsoft\\.sqlserver\\.jdbc",
        "Pdo\\[./_\\](Mssql|SqlSrv)",
        "SQL(Srv|Server)Exception",
        "Unclosed quotation mark after the character string",
        "Microsoft Access (\\d+ )?Driver",
        "JET Database Engine",
        "Access Database Engine",
        "ODBC Microsoft Access",
        "Syntax error \\(missing operator\\) in query expression",
        "\bORA-\\d{5}",
        "Oracle error",
        "Oracle.*?Driver",
        "Warning.*?\\W(oci|ora)_",
        "quoted string not properly terminated",
        "SQL command not properly ended",
        "macromedia\\.jdbc\\.oracle",
        "oracle\\.jdbc",
        "Zend_Db_(Adapter|Statement)_Oracle_Exception",
        "Pdo\\[./_\\](Oracle|OCI)",
        "OracleException",
        "CLI Driver.*?DB2",
        "DB2 SQL error",
        "\bdb2_\\w+\\(",
        "SQLCODE[=:\\d, -]+SQLSTATE",
        "com\\.ibm\\.db2\\.jcc",
        "Zend_Db_(Adapter|Statement)_Db2_Exception",
        "Pdo\\[./_\\]Ibm",
        "DB2Exception",
        "ibm_db_dbi\\.ProgrammingError",
        "Warning.*?\\Wifx_",
        "Exception.*?Informix",
        "Informix ODBC Driver",
        "ODBC Informix driver",
        "com\\.informix\\.jdbc",
        "weblogic\\.jdbc\\.informix",
        "Pdo\\[./_\\]Informix",
        "IfxException",
        "Dynamic SQL Error",
        "Warning.*?\\Wibase_",
        "org\\.firebirdsql\\.jdbc",
        "Pdo\\[./_\\]Firebird",
        "SQLite/JDBCDriver",
        "SQLite\\.Exception",
        "(Microsoft|System)\\.Data\\.SQLite\\.SQLiteException",
        "Warning.*?\\W(sqlite_|SQLite3::)",
        "\\[SQLITE_ERROR\\]",
        "SQLite error \\d+:",
        "sqlite3.OperationalError:",
        "SQLite3::SQLException",
        "org\\.sqlite\\.JDBC",
        "Pdo\\[./_\\]Sqlite",
        "SQLiteException",
        "SQL error.*?POS([0-9]+)",
        "Warning.*?\\Wmaxdb_",
        "DriverSapDB",
        "-3014.*?Invalid end of SQL statement",
        "com\\.sap\\.dbtech\\.jdbc",
        "\\[-3008\\].*?: Invalid keyword or missing delimiter",
        "Warning.*?\\Wsybase_",
        "Sybase message",
        "Sybase.*?Server message",
        "SybSQLException",
        "Sybase\\.Data\\.AseClient",
        "com\\.sybase\\.jdbc",
        "Warning.*?\\Wingres_",
        "Ingres SQLSTATE",
        "Ingres\\W.*?Driver",
        "com\\.ingres\\.gcf\\.jdbc",
        "Exception (condition )?\\d+\\. Transaction rollback",
        "com\\.frontbase\\.jdbc",
        "Syntax error 1. Missing",
        "(Semantic|Syntax) error [1-4]\\d{2}\\.",
        "Unexpected end of command in statement \\[",
        "Unexpected token.*?in statement \\[",
        "org\\.hsqldb\\.jdbc",
        "org\\.h2\\.jdbc",
        "\\[42000-192\\]",
        "![0-9]{5}![^\n]+(failed|unexpected|error|syntax|expected|violation|exception)",
        "\\[MonetDB\\]\\[ODBC Driver",
        "nl\\.cwi\\.monetdb\\.jdbc",
        "Syntax error: EncounteCYAN",
        "org\\.apache\\.derby",
        "ERROR 42X01",
        ", Sqlstate: (3F|42).{3}, (Routine|Hint|Position):",
        "/vertica/Parser/scan",
        "com\\.vertica\\.jdbc",
        "org\\.jkiss\\.dbeaver\\.ext\\.vertica",
        "com\\.vertica\\.dsi\\.dataengine",
        "com\\.mckoi\\.JDBCDriver",
        "com\\.mckoi\\.database\\.jdbc",
        "&lt;REGEX_LITERAL&gt;",
        "com\\.facebook\\.presto\\.jdbc",
        "io\\.prestosql\\.jdbc",
        "com\\.simba\\.presto\\.jdbc",
        "UNION query has different number of fields: \\d+, \\d+",
        "Altibase\\.jdbc\\.driver",
        "com\\.mimer\\.jdbc",
        "Syntax error,[^\n]+assumed to mean",
        "io\\.crate\\.client\\.jdbc",
        "encounteCYAN after end of query",
        "A comparison operator is requiCYAN here",
        "-10048: Syntax error",
        "rdmStmtPrepare\\(.+?\\) returned",
        "SQ074: Line \\d+:",
        "SR185: Undefined procedure",
        "SQ200: No table ",
        "Virtuoso S0002 Error",
        "\\[(Virtuoso Driver|Virtuoso iODBC Driver)\\]\\[Virtuoso Server\\]"]

    my_list = []
    # check for sql injection in url
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
            for sql in mal_sql:
                check_sql = re.search(sql, my_request)
                if check_sql:
                    print(RED + f"True: {new_url}")
                    my_list.append(new_url)
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False: {new_url}")

        except:
            continue

    # check for sql injection in headers
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + f"checking headers: {my_url} {mal}:{mal}")
        try:
            if tor:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, proxies=tor_proxy, timeout=(60,120)).text

            else:
                my_request = web_session.get(my_url, verify=False, headers={"User-Agent": return_user_agent(), mal:mal}, timeout=(5,30)).text

            alert = False
            for sql in mal_sql:
                check_sql = re.search(sql, my_request)
                if check_sql:
                    print(RED + f"True headers: {my_url} {mal}:{mal}")
                    my_list.append(f"headers: {my_url} {mal}:{mal}")
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False headers: {my_url} {mal}:{mal}")

        except:
            continue

    # check for sql injection in cookies
    for mal in other_mal_payloads:
        time.sleep(delay)
        print(CYAN + f"checking cookie: {my_url} {mal}:{mal}")
        try:
            if tor:
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, proxies=tor_proxy, timeout=(60,120)).text

            else:
                my_request = web_session.get(my_url, verify=False, cookies={mal:mal}, headers={"User-Agent": return_user_agent()}, timeout=(5,30)).text

            alert = False
            for sql in mal_sql:
                check_sql = re.search(sql, my_request)
                if check_sql:
                    print(RED + f"True cookies: {my_url} {mal}:{mal}")
                    my_list.append(f"cookies: {my_url} {mal}:{mal}")
                    alert = True
                    break

            if not alert:
                print(GREEN + f"False cookies: {my_url} {mal}:{mal}")

        except:
            continue

    # check for sql injection in forms
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
                for sql in mal_sql:
                    check_sql = re.search(sql, my_request)
                    if check_sql:
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
