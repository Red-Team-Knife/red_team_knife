import threading
import subprocess, os, json, shutil, time

from utils.commands import build_command_string
from controllers.controller_thread import Controller, CommandThread
from controllers.searchsploit import SearchsploitController
import xmltodict

script_options = []
RUNNING_MESSAGE = "Running Nmap vulnerability scan with command: "
TOOL_NAME = "Nmap-Vuln Scan"
SCRIPT_PATH= "nmap-vulners/"
TEMP_FILE_NAME = "tmp/nmap_vuln-temp"

searchsploit_controller = SearchsploitController()


class NmapVulnController(Controller):
    def __init__(self):
        self.last_scan_result = None
        self.is_scan_in_progress = False
        self.tool_name = TOOL_NAME

    def run(self, target, options):
        self.last_scan_result = None

        command = [
            "nmap",
            "--script",
            SCRIPT_PATH,
            "-sV",
            "-oX",
            TEMP_FILE_NAME,
            target
        ]

        command_string = build_command_string(command)

        print(RUNNING_MESSAGE + command_string[:-1]) 

        class NmapCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    try:
                        os.remove(TEMP_FILE_NAME)
                    except:
                        print("Couldn't remove temp Nmap file.")
        self.thread = NmapCommandThread(command, self)
        self.thread.start()

    def __format_result__(self):
        if not self.last_scan_result:

            with open(TEMP_FILE_NAME, "r") as file:

                xml_dict = xmltodict.parse(file.read())

                json_string = json.dumps(xml_dict)

                json_objects = json.loads(json_string)
                json_objects = json_objects["nmaprun"]["host"]["ports"]["port"]
            
            os.remove(TEMP_FILE_NAME)

            with open("tmp.json", "w") as file:
                print(json.dumps(self.last_scan_result), file=file)



            self.last_scan_result = json_objects

        return self.__format_html__()


    def __format_html__(self):

        html_string = ''
        vuln_table_count = 1
        modal_string = ''
        # build port details table
        for port_table in self.last_scan_result:
            html_string += '<b>Port:</b>'
            html_string += '<table>'
            html_string += '<tr>'

            if port_table.get("script", False):
                script_table = port_table.pop("script")

            # build table headers
            for header in port_table.keys():
                html_string += '<th>{}</th>'.format(header.replace("@", ""))
            html_string += '</tr>\n'

            # add rows
            html_string += '<tr>'
            for row in port_table:

                # check subdictionary
                if type(port_table[row]) is dict:
                    html_string += '<td>'
                    # fill field with subdictionary values
                    for subkey in port_table[row]:
                        html_string += f'<b>{subkey.replace("@", "")}: </b>'

                        if type(port_table[row][subkey]) is list:
                            html_string += f"{ ', '.join(port_table[row][subkey])} <br>"
                        else:
                            html_string += f'{port_table[row][subkey]} <br>'
                    html_string += '</td>'
                else:
                    html_string += '<td>{}</td>'.format(port_table[row])    
            html_string += "</tr>\n"
            html_string += '</table><br>\n'

            # build cve table
            if script_table:

                row_vuln_count = 1

                # initializing table
                if type(script_table) is list:
                    filtered_list = []

                    for element in script_table:
                        if element.get("table", False):
                            filtered_list.append(element)
                    html_string += '<b>Vulns:</b>'
                    html_string += '<table class="vuln_table">'    
                    html_string += '<tr>'

                    cve_table = filtered_list[0]["table"]
                    cve_table = cve_table.get("table")
                
                elif not script_table.get("table"):
                    html_string += "<b>No Vulns Found</b><br><br>"
                    break

                else:
                    html_string += '<b>Vulns:</b>'
                    html_string += '<table class="vuln_table">'  
                    html_string += '<tr>'
                    cve_table = script_table["table"]
                    cve_table = cve_table.get("table")

                vuln_table_count += 1

                # sort vuln list for "is_exploit" attr
                cve_table = sorted(cve_table, key=lambda x: 0 if next(item['#text'] for item in x['elem'] if item['@key'] == 'is_exploit') == "true" else 1)

                # build headers
                for header in cve_table[0]["elem"]:
                    html_string += '<th>{}</th>'.format(header['@key'].replace("@", ""))
                html_string += '</tr>'

                for row in cve_table:

                    # highlighting row if attr is_exploit is true
                    if next(elem['#text'] for elem in row['elem'] if elem['@key'] == 'is_exploit') == "true":
                        html_string += f'<tr class = open>'
                    else:
                        html_string += f'<tr>'

                    for elem in row['elem']:
                        html_string += '<td>{}</td>'.format(elem["#text"])

                        # check if cve id attr
                        if (elem["@key"] == 'id'):
                            if "CVE" in elem["#text"] or "EDB" in elem["#text"]:
                                modal_string += self.__build_modal__(modal_string, elem['#text'], vuln_table_count, row_vuln_count)
                    
                    html_string += '</tr>' 
                    row_vuln_count += 1

                html_string += '</table><br><br>'
                            
        return html_string          

    def __build_modal__(self, modal_string, query, vuln_table_count, row_vuln_count):
        modal_string += f'<div id= vuln_table_{vuln_table_count}_vuln_row_{row_vuln_count} class="modal">\t'
        modal_string += '<div class = "modal-content> <span class = "close">&times;</span>'

        print(query)

        searchsploit_controller.run(query)

        '''while (searchsploit_controller.is_scan_in_progress):
            print("Waiting for Vulnerability detail")
            time.sleep(1)'''
        
        content = searchsploit_controller.get_formatted_results()

        modal_string += content
        modal_string += '</div> </div>\n'

        return modal_string 



            


        

