from controllers.sqlmap import (
    EXECUTE_CMD_COMMAND,
    EXECUTE_CMD_MSG,
    EXECUTE_COMMAND,
    OS_SHELL,
    OS_SHELL_COMMAND,
    OS_SHELL_MSG,
    PWN_SHELL,
    PWN_SHELL_COMMAND,
    PWN_SHELL_MSG,
    RADIO_SHELLS,
    REQUEST_DATA,
    SQL_SHELL,
    SQL_SHELL_MSG,
)
from views.web_target import WebTargetBlueprint
from utils.utils import render_list_in_dictionary_as_table


class SqlmapBlueprint(WebTargetBlueprint):

    def __format_html__(self, result) -> str:
        html_output = ""
        output = result.get("output", [])
        os_shell = result.get(OS_SHELL)
        shell_option = result.get(RADIO_SHELLS)
        data = result.get(REQUEST_DATA)
        target = result.get("target")

        # Handling Shell Options Display
        if os_shell:
            if shell_option == OS_SHELL:
                html_output += f"<p>{OS_SHELL_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += OS_SHELL_COMMAND.format(target, data)
            elif shell_option == PWN_SHELL:
                html_output += f"<p>{PWN_SHELL_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += PWN_SHELL_COMMAND.format(target, data)
            elif shell_option == SQL_SHELL:
                html_output += f"<p>{SQL_SHELL_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += OS_SHELL_COMMAND.format(target, data)
            elif shell_option == EXECUTE_COMMAND:
                html_output += f"<p>{EXECUTE_CMD_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += EXECUTE_CMD_COMMAND.format(target, data)
            html_output += "</textarea><br><br>"

        # CRITICAL SECTION: Robust output validation
        if not output:
            return html_output + "<h3>No results detected or target is not vulnerable.</h3>"

        for db in output:
            if isinstance(db, str):
                html_output += "<b> Results: </b><br>"
                html_output += f"<textarea readonly class= 'exploit_textarea'> {db} </textarea>"
            elif isinstance(db, dict):
                # Use list(db.keys())[0] only if db has keys
                keys = list(db.keys())
                if keys:
                    html_output += f"<b> {keys[0]} :</b> <br><br>"

                    for section in db:
                        # FIX: Check if db[section] is a dictionary before iterating
                        if isinstance(db[section], dict):
                            for table in db[section]:
                                html_output += f"<b> {table} :</b>"
                                table_data = db[section][table]
                                # Check that table_data is a list and not empty
                                if isinstance(table_data, list) and len(table_data) > 0:
                                    html_output += "<table>"
                                    html_output += render_list_in_dictionary_as_table(table_data)
                                    html_output += "</table> <br>"
                                else:
                                    html_output += "<p> No data retrieved </p><br>"
                        else:
                            # If not a dictionary, print value as string to avoid crashes
                            html_output += f"<p> {db[section]} </p>"

            html_output += "<br><br>"

        return html_output
