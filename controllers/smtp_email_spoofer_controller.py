from controllers.base_controller import Controller
from controllers.command_thread import CommandThread


NOAUTH = "no_auth"
USERNAME = "username"
PASSWORD = "password"

HOST = "host"
PORT = "port"
SENDER = "sender"
NAME = "name"
RECIPIENTS = "recipients"
SUBJECT = "subject"
BODY = "body"

TOOL_FOLDER = "tools/smtp-email-spoofer-py"
TOOL_DISPLAY_NAME = "SMTP email spoofer"
TOOL_NAME = "smtp_email_spoofer"
TEMP_FILE_NAME = "tmp/smtp-email-spoofer-temp"

scan_options = [
    ("Set Noauth", "checkbox", NOAUTH, ""),
    ("Username", "text", USERNAME, ""),
    ("Password", "password", PASSWORD, ""),
    ("Host", "text", HOST, "Mail server"),
    ("Port", "text", PORT, "Mail server port (SMTP Defaults: 25, 2525, 465, 587)"),
    ("Sender", "text", SENDER, "Sender address"),
    ("Name", "text", NAME, "Sender disply name"),
    (
        "Recipients",
        "text",
        RECIPIENTS,
        "Recipients, space separated (victim1@domain.com victim2@domani.com ...)",
    ),
    ("Subject", "text", SUBJECT, "Email subject"),
    ("Body", "textarea", BODY, "Email body (html formatted)"),
]


class SmtpEmailSpooferController(Controller):

    def __init__(self):
        super().__init__(TOOL_DISPLAY_NAME, TEMP_FILE_NAME)

    def __build_command__(self, target: str, options: dict):
        
        command = [
            "python3",
            f"{TOOL_FOLDER}/spoof.py",
            "cli",
        ]

        print(command)

        if options.get(NOAUTH, False):
            command.append("--noauth")

        if options.get(USERNAME, None):
            command.extend(["--username", options[USERNAME]])

        if options.get(PASSWORD, None):
            command.extend(["--password", options[PASSWORD]])

        if options.get(HOST, None):
            command.extend(["--host", options[HOST]])

        if options.get(PORT, None):
            command.extend(["--port", options[PORT]])

        if options.get(SENDER, None):
            command.extend(["--sender", options[SENDER]])

        if options.get(NAME, None):
            command.extend(["--name", options[NAME]])


        if options.get(RECIPIENTS, None):
            command.extend(["--recipients", options[RECIPIENTS]])

        if options.get(SUBJECT, None):
            command.extend(["--subject", options[SUBJECT]])

        if options.get(BODY, None):
            with open(TEMP_FILE_NAME, "w") as file:
                print(options[BODY], file=file)
                command.extend(["--filename", file.name])

        return command

    def __run_command__(self, command):
        class SmtpEmailSpooferCommandThread(CommandThread):
            def run(self):
                super().run()
                if self._stop_event.is_set():
                    self.calling_controller.__remove_temp_file__()

        return SmtpEmailSpooferCommandThread(command, self)
    
    def __format_result__(self):
        self.__remove_temp_file__()
        return '<p>Operation completed, check terminal for more inforamtion.</p>'