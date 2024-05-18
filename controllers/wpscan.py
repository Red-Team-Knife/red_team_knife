import json
from threading import Thread
from typing import Tuple
from controllers.base_controller import Controller
from controllers.command_thread import CommandThread
from loguru import logger as l

from utils.utils import render_dictionary_as_table, render_list_as_bullet_list, render_list_in_dictionary_as_table


TOOL_DISPLAY_NAME = "WPscan"
TOOL_NAME = "wpscan"
TEMP_FILE_NAME = "tmp/wpscan-temp.json"

OPTIONS_FIRST_MIXED = [("mixed", "mixed"), ("passive", "passive"), ("aggressive","aggressive")]
OPTIONS_FIRST_PASSIVE = [("passive", "passive"), ("mixed", "mixed"), ("aggressive","aggressive")]
PSWD_ATTACK_OPTIONS = [("wp-login","wp-login"), ("xmlrpc", "xmlrpc") , ("xmlrpc-multicall", "xmlrpc-multicall")]

DETECTION_MODE = "detection_mode"
SET_USER_AGENT = "set_user_agent"
SET_RANDOM_UA = "set_random_ua"
HTTP_AUTH = "http_auth"
SET_THREADS = "set_threads"
SET_THROTTLE = "set_throttle"
REQUEST_TIMEOUT = "request_timeout"
CONNECTION_TIMEOUT = "connection_timeout"
DISABLE_SSL = "disable_ssl"
SET_PROXY = "set_proxy"
SET_PROXY_AUTH = "set_proxy_auth"
SET_COOKIE = "set_cookie"
SET_COOKIE_JAR = "set_cookie_jar"
SET_FORCE = "set_force"
SET_WP_DIR = "set_wp_dir"
SET_WP_PLUGINS_DIR = "set_wp_plugins_dir"
SET_ENUMERATION = "set_enumeration"
EN_VULN_PLUGINS = "en_vuln_plugins"
EN_ALL_PLUGINS = "en_all_plugins"
EN_POPULAR_PLUGINS = "en_popular_plugins"
EN_VULN_THEMES = "en_vuln_themes"
EN_ALL_THEMES = "en_all_themes"
EN_POPULAR_THEMES = "en_popular_themes"
EN_TIMITHUBMS = "en_timithumbs"
EN_CONFIG_BACKUPS = "en_config_backups"
EN_DB_EXPORTS = "en_db_exports"
EN_UIDS_RANGE = "en_uids_range"
UIDS_RANGE = "uids_range"
EN_MEDIA_IDS_RANGE = "en_media_ids_range"
MEDIA_IDS_RANGE = "media_ids_range"
EXCLUDE_REGEX = "exclude_regex"
PLUGIN_DETECTION_MODE = "plugin_detection_mode"
PLUGIN_VERSION_DETECTION_MODE = "plugin_version_detection_mode"
EXCLUDE_USERNAMES = "exclude_usernames"
PSWD_FILE_PATH = "pswd_file_path"
LIST_USERNAMES = "list_usernames"
XMLRPC_MAX_NUMBER = "xmlrpc_max_number"
ENABLE_PSWD_ATTACK = "enable_pswd_attack"
PASSWORD_ATTACK_MODE = "password_attack_mode"
LOGIN_URI = "login_uri"
SET_STEALTH = "set_stealth"
API_KEY = "api_key"


scan_option = [
    ("Set Api Key", "text", API_KEY, ""),
    ("Set Detection Mode", "select", DETECTION_MODE, OPTIONS_FIRST_MIXED),
    ("Set a User Agent", "text", SET_USER_AGENT, ""),
    ("Use a Random User Agent", "checkbox", SET_RANDOM_UA, ""),
    ("Set HTTP Credentials", "text", HTTP_AUTH, "login:password"),
    ("Set Threads to use", "number", SET_THREADS, "Default 5"),
    ("Set Milliseconds to wait in the request", "number", SET_THROTTLE, ""),
    ("Set Request Timeout seconds", "number", REQUEST_TIMEOUT, "Default: 60"),
    ("Set Connection Timeout seconds", "number", CONNECTION_TIMEOUT, "Default: 30"),
    ("Disable SSL/TLS Certificates", "checkbox", DISABLE_SSL, ""),
    ("Set Proxy", "text", SET_PROXY, "protocol://IP:port"),
    ("Set Proxy Auth", "text", SET_PROXY_AUTH, "login:password"),
    ("Set Cookie", "text", SET_COOKIE, "cookie= content"),
    ("Set Cookie Jar Filepath", "text", SET_COOKIE_JAR, "Default /tmp/wpscan/cookie_jar.txt"),
    ("Disable control over Wordpress Wxecution on target", "checkbox", SET_FORCE, ""),
    ("Set Wordpress Content directory", "text", SET_WP_DIR, "wp-content"),
    ("Set Wordpress plugin directory", "text", SET_WP_PLUGINS_DIR, "wp-content/plugins"),
    ("Set Enumeration Processes (Default: All Plugins, Config Backups)", "checkbox", SET_ENUMERATION, ""),
    ("Enumerate Vulnerable plugins", "checkbox", EN_VULN_PLUGINS, ""),
    ("Enumerate All plugins", "checkbox", EN_ALL_PLUGINS, ""),
    ("Enumerate Popular plugins", "checkbox", EN_POPULAR_PLUGINS, ""),
    ("Enumerate Vulnerable themes", "checkbox", EN_VULN_THEMES, ""),
    ("Enumerate All themes", "checkbox", EN_ALL_THEMES, ""),
    ("Enumerate Popular themes", "checkbox", EN_POPULAR_THEMES, ""),
    ("Enumerate Timithumbs", "checkbox", EN_TIMITHUBMS, ""),
    ("Enumerate Config backups", "checkbox", EN_CONFIG_BACKUPS, ""),
    ("Enumerate DB exports", "checkbox", EN_DB_EXPORTS, ""),
    ("Enumerate User IDs range", "checkbox", EN_UIDS_RANGE, ""),
    ("Range", "text", UIDS_RANGE, "Default: 1-10"),
    ("Enumerate Media IDs range", "checkbox", EN_MEDIA_IDS_RANGE, ""),
    ("Range", "text", MEDIA_IDS_RANGE, "Default: 1-15"),
    ("Exclude Response content", "text", EXCLUDE_REGEX, "insert regex"),
    ("Plugin Detection Mode", "select", PLUGIN_DETECTION_MODE, OPTIONS_FIRST_PASSIVE),
    ("Plugin Version Detection Mode", "select", PLUGIN_VERSION_DETECTION_MODE, OPTIONS_FIRST_MIXED),
    ("Exclude Usernames", "text", EXCLUDE_USERNAMES, "insert regex"),
    ("Set Password File Path to use", "text", PSWD_FILE_PATH, "path/to/your/file"),
    ("Set Usernames List to use", "text", LIST_USERNAMES, "a1,a2,a3"),
    ("Set Maximum number of passwords to send by request", "number", XMLRPC_MAX_NUMBER, "Default: 500"),
    ("Enable Password Attack mode", "checkbox", ENABLE_PSWD_ATTACK, ""),
    ("Set Password Attack mode", "select", PASSWORD_ATTACK_MODE, PSWD_ATTACK_OPTIONS),
    ("Set Login URI", "text", LOGIN_URI, "Default: /wp-login.php"),
    ("Set Stealth mode", "checkbox", SET_STEALTH, ""),
]

class WPscanController(Controller):
    
    def __init__(self):
        super().__init__(TOOL_NAME, TEMP_FILE_NAME)
        
    def __build_command__(self, target: str, options: dict) -> list:
        
        command = [
            "wpscan",
            "--url",
            target,
            "-o",
            "./" + TEMP_FILE_NAME,
            "-f",
            "json",
        ]
        
        if options.get(API_KEY, False):
            command.extend(["--api-token", options[API_KEY]])
        if options.get(DETECTION_MODE, False):
            command.extend(["--detection-mode", options[DETECTION_MODE]])
        if options.get(SET_USER_AGENT, False):
            command.extend(["--ua", options[SET_USER_AGENT]])
        if options.get(SET_RANDOM_UA, False):
            command.append("--rua")
        if options.get(HTTP_AUTH, False):
            command.extend(["--http-auth", options[HTTP_AUTH]])
        if options.get(SET_THREADS, False):
            command.extend(["--max-threads", options[SET_THREADS]])
        if options.get(SET_THROTTLE, False):
            command.extend(["--throttle", options[SET_THROTTLE]])
        if options.get(REQUEST_TIMEOUT, False):
            command.extend(["--request-timeout", options[REQUEST_TIMEOUT]])
        if options.get(CONNECTION_TIMEOUT, False):
            command.extend(["--connect-timeout", options[CONNECTION_TIMEOUT]])
        if options.get(DISABLE_SSL, False):
            command.append("--disable-tls-checks")
        if options.get(SET_PROXY, False):
            command.extend(["--proxy", options[SET_PROXY]])
        if options.get(SET_PROXY_AUTH, False):
            command.extend(["--proxy-auth", options[SET_PROXY_AUTH]])
        if options.get(SET_COOKIE, False):
            command.extend(["--cookie-string", options[SET_COOKIE]])
        if options.get(SET_COOKIE_JAR, False):
            command.extend(["--cookie-jar", options[SET_COOKIE_JAR]])
        if options.get(SET_FORCE, False):
            command.append("--force")
        if options.get(SET_WP_DIR, False):
            command.extend(["--wp-content-dir", options[SET_WP_DIR]])
        if options.get(SET_WP_PLUGINS_DIR, False):
            command.extend(["--wp-plugins-dir", options[SET_WP_PLUGINS_DIR]])
        if options.get(SET_ENUMERATION, False):
            command.append("--enumerate")
            en = ''
            if options.get(EN_VULN_PLUGINS, False):
                en += 'vp'
            if options.get(EN_ALL_PLUGINS, False):
                en += 'ap'
            if options.get(EN_POPULAR_PLUGINS, False):
                en += ',p'
            if options.get(EN_VULN_THEMES, False):
                en += ',vt'
            if options.get(EN_ALL_THEMES, False):
                en += ',at'
            if options.get(EN_POPULAR_THEMES, False):
                en += ',t'
            if options.get(EN_TIMITHUBMS, False):
                en += ',tt'
            if options.get(EN_CONFIG_BACKUPS, False):
                en += ',cb'
            if options.get(EN_DB_EXPORTS, False):
                en += ',dbe'
            if options.get(EN_UIDS_RANGE, False):
                en += ',u'
                if options.get(UIDS_RANGE, False):
                    en += options[UIDS_RANGE]
            if options.get(EN_MEDIA_IDS_RANGE, False):
                en += ',m'
                if options.get(MEDIA_IDS_RANGE, False):
                    en += options[MEDIA_IDS_RANGE]
            command.append(en)
        if options.get(EXCLUDE_REGEX, False):
            command.extend(["--exclude-content-based", options[EXCLUDE_REGEX]])
        if options.get(PLUGIN_DETECTION_MODE, False):
            command.extend(["--plugins-detection", options[PLUGIN_DETECTION_MODE]])
        if options.get(PLUGIN_VERSION_DETECTION_MODE, False):
            command.extend(["--plugins-version-detection", options[PLUGIN_VERSION_DETECTION_MODE]])
        if options.get(EXCLUDE_USERNAMES, False):
            command.extend(["--exclude-usernames", options[EXCLUDE_USERNAMES]])
        if options.get(PSWD_FILE_PATH, False):
            command.extend(["--passwords", options[PSWD_FILE_PATH]])
        if options.get(LIST_USERNAMES, False):
            command.extend(["--usernames", options[LIST_USERNAMES]])
        if options.get(XMLRPC_MAX_NUMBER, False):
            command.extend(["--multicall-max-passwords", options[XMLRPC_MAX_NUMBER]])
        if options.get(ENABLE_PSWD_ATTACK, False):
            command.append("--password-attack")
            if options.get(PASSWORD_ATTACK_MODE, False):
                command.append(options[PASSWORD_ATTACK_MODE])
        if options.get(LOGIN_URI, False):
            command.extend(["--login-uri", options[LOGIN_URI]])
        if options.get(SET_STEALTH, False):
            command.append("--stealthy")
        
        return command
    
    def __run_command__(self, command) -> Thread:
        class WpscanCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__()
                    
        return WpscanCommandThread(command, self)
    
    def __parse_temp_results_file__(self) -> Tuple[object, Exception]:        
        with open(TEMP_FILE_NAME, "r") as file:
            try:
                data:dict = json.load(file)
            except Exception as e:
                return None, e
        with open ("test.json","w") as file:
            print(json.dumps(data), file= file)
        return data, None
    
    def __format_html__(self) -> str:
        html_output = ""
        html_output += "<b>General Infos</b><br>\n"
        html_output += f"<p><b>Target url:</b> {self.last_scan_result['target_url']}</p>\n"
        html_output += f"<p><b>Target ip:</b> {self.last_scan_result['target_ip']}</p>\n"
        html_output += f"<p><b>Effective url:</b> {self.last_scan_result['effective_url']}</p><br>\n"
        
        interesting_findings = self.last_scan_result.get("interesting_findings", None)
        if interesting_findings:
            html_output += "<b>Interesting Findings</b><br>\n"
            
            html_output += "<table>\n"
            html_output += "<tr>\n"
            for header in interesting_findings[0].keys():
                html_output += f"<th>{header}</th>\n"
            html_output += "</tr>\n"
            for row in interesting_findings:
                html_output += "<tr>\n"
                
                for column in row:
                    html_output += "<td>\n"
                    if isinstance(row[column], dict):
                        html_output += f"<table>\n{render_dictionary_as_table(row[column])}</table>\n"
                    elif isinstance(row[column], list):
                        html_output += f"<ul>\n{render_list_as_bullet_list(row[column])}</ul>\n"
                    else:
                        html_output += f"{row[column]}\n"
                    html_output += "</td>\n"
                html_output += "</tr>\n"
                
            html_output += "</table><br><br>\n"
            
        version = self.last_scan_result.get("version", None)
        if version:
            html_output += '<b>Verison Details</b><br>\n'
            for tag, detail in version.items():
                if isinstance(detail, dict):
                    html_output += f"<b>{tag}:</b><table>\n{render_dictionary_as_table(detail)}</table>\n" 
                if isinstance(detail, list):
                    if isinstance(detail[0], dict):
                        html_output += f"<table>\n{render_list_in_dictionary_as_table(detail)}</table>\n" 
                    else:
                        html_output += f"<b>{tag}:</b><ul>\n{render_list_as_bullet_list(detail)}</ul>\n"
                        
        
        main_theme = self.last_scan_result.get("main_theme", None)
        if main_theme:
            html_output += "<b>Main Theme</b><br>\n"
            for tag, detail in main_theme.items():
                if isinstance(detail, dict):
                    html_output += f"<b>{tag}:</b><table>\n{render_dictionary_as_table(detail)}</table>\n" 
                elif isinstance(detail, list):
                    html_output += f"<b>{tag}:</b><ul>\n{render_list_as_bullet_list(detail)}</ul>\n"
                    html_output += "<br>\n"
                else:
                    html_output += f"<p><b>{tag}:</b> {detail}</p>\n"
        
        plugins: dict = self.last_scan_result.get("plugins")
        if plugins:
            html_output += "<b>Plugins</b><br>\n"
            html_output += "<table>\n"
            html_output += "<tr>\n"
            first_plugin = next(iter(plugins.keys()))
            for header in plugins[first_plugin].keys():
                html_output += f"<th>{header}</th>\n"
            html_output += "</tr>\n"
            
            for plugin in plugins:
                html_output += "<tr>\n"
                for tag, detail in plugins[plugin].items():
                    html_output += "<td>\n" 
                    if isinstance(detail, dict):
                        html_output += "<table>\n"
                        html_output += render_dictionary_as_table(detail)
                        html_output += "</table>\n"
                    elif isinstance(detail, list):
                        if tag == "vulnerabilities":
                            if len(detail) == 0:
                                html_output += "No Vulnerability Found\n"
                            else:
                                html_output += f"<table>\n{render_list_in_dictionary_as_table(detail)}</table>\n" 
                    else:
                        html_output += f"{detail}\n"
                    html_output += "</td>\n" 
                html_output += "</tr>\n" 
                
            html_output += "</table><br><br>\n" 
            
            themes = self.last_scan_result.get("themes", None)
            if themes:
                html_output += "<b>Themes</b><br>\n"
                html_output += "<table>\n"
                html_output += "<tr>\n"
                first_theme = next(iter(themes.keys()))
                for header in themes[first_theme].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"
                
                for theme in themes:
                    html_output += "<tr>\n"
                    for tag, detail in themes[theme].items():
                        html_output += "<td>\n" 
                        if isinstance(detail, dict):
                            html_output += "<table>\n"
                            html_output += render_dictionary_as_table(detail)
                            html_output += "</table>\n"
                        elif isinstance(detail, list):
                            if tag == "vulnerabilities":
                                if len(detail) == 0:
                                    html_output += "No Vulnerability Found\n"
                                else:
                                    html_output += f"<table>\n{render_list_in_dictionary_as_table(detail)}</table>\n" 
                        else:
                            html_output += f"<p>{detail}</p>\n"
                        html_output += "</td>\n" 
                    html_output += "</tr>\n" 
                
                html_output += "</table><br><br>\n"                    
            
            timthumbs = self.last_scan_result.get("timthumbs", None)
            if timthumbs:
                html_output += "<b>Timthumbs</b><br>\n"
                html_output += f"<table>\n{render_dictionary_as_table(timthumbs)}</table><br><br>\n"               
            
            config_backups = self.last_scan_result.get("config_backups", None)
            if config_backups:
                html_output += "<b>Configurations Backups</b><br>\n"
                html_output += f"<table>\n{render_dictionary_as_table(config_backups)}</table><br><br>\n"
                
            db_exprorts = self.last_scan_result.get("db_exports", None)
            if db_exprorts:
                html_output += "<b>DB Exports</b><br>\n"
                html_output += f"<table>\n{render_dictionary_as_table(db_exprorts)}</table><br><br>\n"  
                
            medias = self.last_scan_result.get("medias", None)
            if medias:
                html_output += "<b>Medias</b><br>"
                html_output += "<table>"
                html_output += "<tr>\n"
                first_media = next(iter(medias.keys()))
                html_output += "<th>media_id</th>"
                for header in medias[first_media].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"
                
                for media in medias:
                    html_output += "<tr>\n"
                    html_output += f"<td>{media}</td>"
                    for tag, detail in medias[media].items():
                        html_output += f"<td>{detail}</td>\n" 
                    html_output += "</tr>\n" 
                    
                html_output += "</table><br><br>\n"
            
            users = self.last_scan_result.get("users", None)
            if users:
                html_output += "<b>Users</b><br>"
                html_output += "<table>"
                html_output += "<tr>\n"
                first_user = next(iter(users.keys()))
                html_output += "<th>user_id</th>"
                for header in users[first_user].keys():
                    html_output += f"<th>{header}</th>\n"
                html_output += "</tr>\n"
                
                for user in users:
                    html_output += "<tr>\n"
                    html_output += f"<td>{user}</td>"
                    for tag, detail in users[user].items():
                        html_output += f"<td>{detail}</td>\n" 
                    html_output += "</tr>\n" 
                    
                html_output += "</table><br><br>\n"  
                
            api_detail = self.last_scan_result.get("vuln_api", None)
            if api_detail:
                html_output += "<b>Api Details</b><br>"
                for tag, detail in api_detail.items():
                    html_output += f"<p><b>{tag}: </b>{detail}</p>"                            
            
        return html_output