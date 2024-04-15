import subprocess, os, json, shutil
from utils.dict import remove_empty_values
from utils.commands import build_command_string

# constants also used in the html template
LIMIT = "result_limit"
LIMIT_ENABLE = "result_limit_enable"
OFFSET = "offset"
PROXY = "proxy"
SHODAN = "shodan"
SCREENSHOT = "screenshot"
DNS_RESOLUTION = "dns_resolution"
DNS_SERVER = "dns_server"
TAKEOVER_CHECK = "takeover_check"
SUBDOMAIN_RESOLUTION = "subdomain_resolution"
DNS_LOOKUP = "dns_lookup"
DNS_BRUTEFORCE = "dns_bruteforce"
SOURCE = "source"

TEMP_FILE_NAME = "the-harvester-temp"
SCREENSHOTS_DIRECTORY = "screenshots"

RUNNING_MESSAGE = "Running theHarvester with command: "




# TODO add suppport for API keys

class TheHarvester:
    def __init__(self):
        self.scan_result = None

    def run(self,domain, options: dict):

        screenshot_saved= False

        # check screenshot folder existance
        screenshot_folder = os.path.abspath(SCREENSHOTS_DIRECTORY)
        if not os.path.exists(screenshot_folder):
            os.makedirs(SCREENSHOTS_DIRECTORY)
        else:
            shutil.rmtree(SCREENSHOTS_DIRECTORY)
            os.makedirs(SCREENSHOTS_DIRECTORY)

        # build command
        command = ["theHarvester", "-d", domain, "-f", TEMP_FILE_NAME]


        if options.get(SOURCE, False):
            command.append("-b")
            command.append(options.get(SOURCE))
        else:
            command.append("-b")
            command.append("all")

        if options.get(LIMIT, False):
            command.append("-l")
            command.append(options.get(LIMIT))

        if options.get(OFFSET, False):
            command.append("-S")
            command.append(options.get(OFFSET))

        if options.get(PROXY, False):
            command.append("-p")
            command.append(options.get(PROXY))

        if options.get(SHODAN, False):
            command.append("-s")
            command.append(options.get(SHODAN))

        if options.get(SCREENSHOTS_DIRECTORY, False):
            command.append("--screenshot")
            command.append(options.get(SCREENSHOTS_DIRECTORY))
            screenshot_saved = True

        if options.get(DNS_SERVER, False):
            command.append("-e")
            command.append(options.get(DNS_SERVER))

        if options.get(TAKEOVER_CHECK, False):
            command.append("-t")

        if options.get(DNS_RESOLUTION, False):
            command.append("-v")

        if options.get(DNS_LOOKUP, False):
            command.append("-n")

        if options.get(DNS_BRUTEFORCE, False):
            command.append("-c")

        if options.get(SUBDOMAIN_RESOLUTION, False):
            command.append("-r")

        # log command
        command_string = build_command_string(command)

        print(RUNNING_MESSAGE + command_string[:-1])

        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
            print(output.decode("utf-8"))
            print("\033[0m")
            with open(TEMP_FILE_NAME + ".json", "r") as file:
                data = json.load(file)

            # remove temp files
            os.remove(TEMP_FILE_NAME + ".json")
            os.remove(TEMP_FILE_NAME + ".xml")

            # check if screenshots are available
            if screenshot_saved:
                data["screenshots_available"] = True
            else:
                data["screenshots_available"] = False

            self.scan_result = data

            # return formatted html
            return self.format_result()
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            print("\033[0m")
            return None


    def format_result(self):

        self.scan_result = remove_empty_values(self.scan_result)

        if not self.scan_result:
            return "<p>No Result Found</p>"

        html_output = ""

        if self.scan_result.get("screenshots_available", False):
            html_output += (
                "<p>Screenshots saved here: "
                + os.path.abspath(SCREENSHOTS_DIRECTORY)
                + "</p><br>"
            )
            self.scan_result.pop("screenshots_available")

        html_output += """
                        <table>
                        """

        for key in self.scan_result.keys():
            html_output += f"""
                <tr>
                    <td><b>{key}</b></td>
                """

            items = ""
            for i in self.scan_result[key]:
                items += i
                items += "<br>"

            # remove last '<br>'
            items = items[:-4]

            html_output += f"""
                <td>{items}</td>
                </tr>
            """
        html_output += "</table>"
        return html_output
