from views.web_target import WebTargetBlueprint
from controllers.commix import (
    OS_SHELL,
    OS_SHELL_MSG,
    OS_SHELL_COMMAND,
    ALTER_SHELL,
    ALTER_SHELL_MSG,
    ALTER_SHELL_COMMAND,
    EXECUTE_COMMAND,
    EXECUTE_CMD_MSG,
    RADIO_SHELLS,
    SET_DATA,
)


class CommixBlueprint(WebTargetBlueprint):
    def __format_html__(self, results) -> str:
        html_output = ""

        if results[OS_SHELL]:
            shell_type = results[RADIO_SHELLS]
            target = results['target']
            data = results[SET_DATA]
            if shell_type == OS_SHELL:
                html_output += f"<p>{OS_SHELL_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += OS_SHELL_COMMAND.format(target, data)
            elif shell_type == ALTER_SHELL:
                html_output += f"<p>{ALTER_SHELL_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += ALTER_SHELL_COMMAND.format(target, data)
            elif shell_type == EXECUTE_COMMAND:
                html_output += f"<p>{EXECUTE_CMD_MSG}</p>"
                html_output += f"<textarea readonly style=\"width: calc(100%); height: 45px; font-family: 'Courier New', Courier, monospace;\"> "
                html_output += EXECUTE_CMD_MSG.format(target, data)

            html_output += "</textarea><br><br>"

        html_output += "<textarea readonly class='exploit_textarea'>"
        html_output += results['text']
        html_output += " </textarea>"

        return html_output
