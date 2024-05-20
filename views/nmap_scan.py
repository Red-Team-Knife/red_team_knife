from views.view import BaseBlueprint
from utils.utils import debug_route, fill_table_column_dict, fill_table_column_list
from flask import request
from controllers.nmap_vuln import (
    TOOL_NAME as NMAP_VULN_NAME,
    TOOL_DISPLAY_NAME as NMAP_VULN_DISPLAY_NAME,
    PORT_RANGE,
)
from controllers.feroxbuster import (
    TOOL_NAME as FEROXBUSTER_NAME,
    TOOL_DISPLAY_NAME as FEROXBUSTER_DISPLAY_NAME,
)
from controllers.w4af_audit import (
    TOOL_NAME as W4AF_TOOL_NAME,
    TOOL_DISPLAY_NAME as W4AF_TOOL_DISPLAY_NAME,
)


class NmapBlueprint(BaseBlueprint):

    def interface(self):
        extra = {
            "nmap_vuln_name": NMAP_VULN_NAME,
            "nmap_vuln_display_name": NMAP_VULN_DISPLAY_NAME,
            "port_range": PORT_RANGE,
            "feroxbuster_name": FEROXBUSTER_NAME,
            "feroxbuster_display_name": FEROXBUSTER_DISPLAY_NAME,
            "w4af_name": W4AF_TOOL_NAME,
            "w4af_display_name": W4AF_TOOL_DISPLAY_NAME,
        }
        return super().interface(extra=extra)
    
    def __format_html__(self, results) -> str:

        html = ""
        if results.get("os", False):
            html = self.__format_os_scan__(results)
        elif results.get("ports", False):
            html = self.__format_port_scan__(results)
        return html

    def __format_os_scan__(self, results):
        html_string = ""

        # build extraports table
        if results["ports"].get("extraports"):
            html_string += "<b>OS scan</b><br>"
            extraports = results["ports"].get("extraports")

            html_string += "<b>Extraports</b><br>"
            html_string += "<table>"
            html_string += "<tr>"

            # build table headers
            for key in extraports:
                html_string += "<th>{}</th>".format(key.replace("@", ""))
            html_string += "</tr>\n"

            html_string += "<tr>"

            # fill table
            for row in extraports:
                if isinstance(extraports[row], dict):
                    html_string += "<td>{}</td>".format(
                        fill_table_column_dict(row, key)
                    )
            html_string += "</table><br>\n"

        # build port table
        if results["ports"].get("port", False):
            port = results["ports"].get("port")

            html_string += "<b>Ports</b><br>"
            html_string += "<table>"
            html_string += "<tr>"

            # build table headers
            for key in port[0].keys():
                html_string += "<th>{}</th>".format(key.replace("@", ""))
            html_string += "</tr>\n"

            # fill table
            for row in port:

                # check if it is printing a port
                if row.get("state"):
                    # check if port is open to highlight row
                    if row["state"]["@state"] == "open":
                        html_string += "<tr class = open>"
                else:
                    html_string += "<tr>"

                for key in row:
                    # check subdictionary
                    if type(row[key]) is dict:
                        html_string += "<td>{}</td>".format(
                            fill_table_column_dict(row, key)
                        )
                    else:
                        html_string += "<td>{}</td>".format(row[key])
                html_string += "</tr>\n"
            html_string += "</table><br>\n"

        if results["os"].get("portused"):
            # build portused table
            portused = results["os"].get("portused")
            html_string += "<b>Ports Used</b><br>"
            html_string += "<table>"
            html_string += "<tr>"

            if isinstance(portused, list):
                for key in portused[0].keys():
                    html_string += "<th>{}</th>".format(key.replace("@", ""))
                html_string += "</tr>\n"
                for row in portused:

                    if row["@state"] == "open":
                        html_string += "<tr class = open>"
                    else:
                        html_string += "<tr>"

                    # fill row
                    for key in row:
                        html_string += "<td>{}</td>".format(row[key])
                    html_string += "</tr>\n"

            else:
                for key in portused.keys():
                    html_string += "<th>{}</th>".format(key.replace("@", ""))
                html_string += "</tr>\n"

                if portused["@state"] == "open":
                    html_string += "<tr class = open>"
                else:
                    html_string += "<tr>"

                for key in portused:
                    html_string += "<td>{}</td>".format(portused[key])
                html_string += "</tr>\n"

            html_string += "</table><br>\n"

        if results["os"].get("osmatch", False):
            # build osmatch table
            osmatch = results["os"].get("osmatch")
            html_string += "<b>Os Match</b><br>"
            html_string += "<table>"
            html_string += "<tr>"

            if isinstance(osmatch, list):
                for key in osmatch[0].keys():
                    html_string += "<th>{}</th>".format(key.replace("@", ""))
                html_string += "</tr>\n"

                for row in osmatch:
                    html_string += "<tr>"

                    for key in row:
                        if isinstance(row[key], dict):
                            html_string += "<td>{}</td>".format(
                                fill_table_column_dict(row, key)
                            )
                        elif isinstance(row[key], list):
                            html_string += "<td>{}</td>".format(
                                fill_table_column_list(row, key)
                            )
                        else:
                            html_string += "<td>{}</td>".format(row[key])
                    html_string += "</tr>"

            else:
                for key in osmatch.keys():
                    html_string += "<th>{}</th>".format(key.replace("@", ""))

                html_string += "</tr>\n"

                html_string += "<tr>"
                # fill table
                for row in osmatch:
                    if isinstance(osmatch[row], dict):
                        html_string += "<td>{}</td>".format(
                            fill_table_column_dict(osmatch, row)
                        )
                    elif isinstance(osmatch[row], list):
                        html_string += "<td>{}</td>".format(
                            fill_table_column_list(osmatch, row)
                        )
                    else:
                        html_string += "<td>{}</td>".format(osmatch[row])
                html_string += "</tr>\n"
            html_string += "</table><br>\n"
        else:
            html_string += "<b> No OS Result Fond </b>"
        return html_string

    def __format_port_scan__(self, results):
        html_string = ""

        # print a table for type of scan
        for type_scan in results:
            html_string += f"<b>{type_scan}</b>"
            html_string += "<table>\n"

            # fetch headers of table
            for scan_subject in results[type_scan]:
                # build table headers
                if isinstance(results[type_scan][scan_subject], list):
                    for key in results[type_scan][scan_subject][0].keys():
                        html_string += "<th>{}</th>".format(key.replace("@", ""))
                else:
                    for key in results[type_scan][scan_subject].keys():
                        html_string += "<th>{}</th>".format(key.replace("@", ""))
                html_string += "</tr>\n"

            for scan_subject in results[type_scan]:
                # add rows in table
                for row in results[type_scan][scan_subject]:
                    # check if it is printing a port
                    if row.get("state"):
                        # check if port is open to highlight row
                        if row["state"]["@state"] == "open":
                            if row["service"]["@name"] in ("http", "https"):
                                html_string += f'<tr class = open onclick="suggestHttpTools()" title="Found an open http/https Port. Click to see tips." style="cursor: pointer;")>'
                            else:
                                html_string += f"<tr class = open onclick=\"redirectToNmapVuln('{row['@portid']}')\" title=\"Found an open Port. Click to try searching for Vulns.\" style=\"cursor: pointer;\")>"
                    else:
                        html_string += "<tr>"

                    for key in row:
                        # check subdictionary
                        if type(row[key]) is dict:
                            html_string += "<td>{}</td>".format(
                                fill_table_column_dict(row, key)
                            )
                        else:
                            html_string += "<td>{}</td>".format(row[key])
                    html_string += "</tr>\n"
            html_string += "</table><br>\n"

        return html_string
