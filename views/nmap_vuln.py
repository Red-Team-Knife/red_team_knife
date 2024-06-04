from views.view import BaseBlueprint
from utils.utils import debug_route
from flask import request
from controllers.exploitation_tips import EXPLOITATION_TIPS_NAME
import copy


class NmapVulnBlueprint(BaseBlueprint):

    def interface(self):
        extra = {"exploitation_tips_name": EXPLOITATION_TIPS_NAME}
        return super().interface(extra=extra)

    def __format_html__(self, results):

        last_scan_result = copy.deepcopy(results)

        if isinstance(last_scan_result, dict):
            last_scan_result = [last_scan_result]

        html_string = ""
        # build port details table
        for port_table in last_scan_result:
            html_string += "<b class='table_bold'>Port:</b>"
            html_string += "<table>"
            html_string += "<tr>"

            if port_table.get("script", False):
                script_table = port_table.pop("script")
            else:
                script_table = None

            # build table headers
            for header in port_table:
                html_string += "<th>{}</th>".format(header.replace("@", ""))
            html_string += "</tr>\n"

            # add rows
            html_string += "<tr>"
            for row in port_table:
                if isinstance(port_table[row], dict):
                    html_string += "<td>"
                    # fill field with subdictionary values
                    for subkey in port_table[row]:
                        html_string += f'<b class="table_bold">{subkey.replace("@", "")}: </b>'

                        if type(port_table[row][subkey]) is list:
                            html_string += f"{ ', '.join(port_table[row][subkey])} <br>"
                        else:
                            html_string += f"{port_table[row][subkey]} <br>"
                    html_string += "</td>"
                else:
                    html_string += "<td>{}</td>".format(port_table[row])
            html_string += "</tr>\n"
            html_string += "</table><br>\n"

            # build cve table
            if script_table:
                # initializing table
                if type(script_table) is list:
                    filtered_list = []

                    for element in script_table:
                        if element.get("table", False):
                            filtered_list.append(element)
                            
                    if len(filtered_list) == 0:
                        break
                    html_string += "<b>Vulns:</b>"
                    html_string += '<table class="vuln_table">'
                    html_string += "<tr>"
                    cve_table = filtered_list[0]["table"]
                    cve_table = cve_table.get("table")

                elif not script_table.get("table"):
                    html_string += "<b class='table_bold'>No Vulns Found</b><br><br>"
                    break

                else:
                    html_string += "<b>Vulns:</b>"
                    html_string += '<table class="vuln_table">'
                    html_string += "<tr>"
                    cve_table = script_table["table"]
                    cve_table = cve_table.get("table")

                if not isinstance(cve_table, list):
                    cve_table = [cve_table]

                # sort vuln list for "is_exploit" attr
                cve_table = sorted(
                    cve_table,
                    key=lambda x: (
                        0
                        if next(
                            item["#text"]
                            for item in x["elem"]
                            if item["@key"] == "is_exploit"
                        )
                        == "true"
                        else 1
                    ),
                )

                # reorder dictionaries
                cve_table = [
                    {
                        "elem": sorted(
                            item["elem"],
                            key=lambda x: ["id", "type", "is_exploit", "cvss"].index(
                                x["@key"]
                            ),
                        )
                    }
                    for item in cve_table
                ]

                # build headers
                for header in cve_table[0]["elem"]:
                    html_string += "<th>{}</th>".format(header["@key"].replace("@", ""))
                html_string += "</tr>"

                for row in cve_table:
                    # Check if the row contains an element with the key "is_exploit"
                    is_exploit = False
                    exploit_available = False
                    for elem in row["elem"]:
                        if elem["@key"] == "id":
                            exploit_available = (
                                "EDB" in elem["#text"] or "CVE" in elem["#text"]
                            ) and "MSF" not in elem["#text"]
                        if elem["@key"] == "is_exploit":
                            is_exploit = elem["#text"] == "true"

                    # Construct the opening tag for the table row
                    if is_exploit:
                        if exploit_available:
                            html_string += "<tr class='exploit_available'>"
                        else:
                            html_string += "<tr class='exploit_less_details'>"
                    else:
                        html_string += "<tr>"

                    # Construct table cells for each element in the row
                    for elem in row["elem"]:
                        if elem["@key"] == "id":
                            html_string += "<td class='vuln_code'>{}</td>".format(
                                elem["#text"]
                            )
                        elif elem["@key"] == "type":
                            html_string += "<td class='vuln_type'>{}</td>".format(
                                elem["#text"]
                            )
                        else:
                            html_string += "<td>{}</td>".format(elem["#text"])

                    # Close the table row
                    html_string += "</tr>"

                html_string += "</table><br><br>"

        return html_string
