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
from views.web_target_view import WebTargetBlueprint
from utils.utils import render_list_in_dictionary_as_table


class SqlmapBlueprint(WebTargetBlueprint):

    def __format_html__(self, result) -> str:
        html_output = ""
        output = result["output"]
        os_shell = result[OS_SHELL]
        shell_option = result[RADIO_SHELLS]
        data = result[REQUEST_DATA]
        target = result["target"]
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

        for db in output:
            if isinstance(db, str):
                html_output += "<b> Results: </b><br>"
                html_output += (
                    f"<textarea readonly class= 'exploit_textarea'> {db} </textarea>"
                )
            else:
                html_output += f"<b> {list(db.keys())[0]} :</b> <br><br>"

                for section in db:
                    for table in db[section]:
                        html_output += f"<b> {table} :</b>"
                        if len(db[section][table]) == 0:
                            html_output += "<p> No data Retrieved </p><br>"
                        else:
                            html_output += "<table>"
                            html_output += render_list_in_dictionary_as_table(
                                db[section][table]
                            )
                            html_output += "</table> <br>"

            html_output += "<br><br>"

        return html_output
