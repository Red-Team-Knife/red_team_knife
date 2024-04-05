import subprocess, os, json, shutil

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

    def run(
        self,
        domain,
        source="all",
        result_limit=None,
        offset=None,
        proxy=None,
        shodan=None,
        screenshot=None,
        dns_resolution_virtual_hosts=None,
        dns_server=None,
        takeover_check=None,
        subdomain_resolution=None,
        dns_lookup=None,
        dns_bruteforce=None,
    ):

        # check screenshot folder existance
        screenshot_folder = os.path.abspath(SCREENSHOTS_DIRECTORY)
        if not os.path.exists(screenshot_folder):
            os.makedirs(SCREENSHOTS_DIRECTORY)
        else:
            shutil.rmtree(SCREENSHOTS_DIRECTORY)
            os.makedirs(SCREENSHOTS_DIRECTORY)

        # build command
        command = ["theHarvester", "-d", domain, "-f", TEMP_FILE_NAME]
        if source:
            command.append("-b")
            command.append(source)
        else:
            command.append("-b")
            command.append("all")

        if self.check_input(result_limit):
            command.append("-l")
            command.append(result_limit)

        if offset != "0":
            command.append("-S")
            command.append(offset)

        if self.check_input(proxy):
            command.append("-p")
            command.append(proxy)

        if self.check_input(shodan):
            command.append("-s")
            command.append(shodan)

        if self.check_input(screenshot):
            command.append("--screenshot")
            command.append(SCREENSHOTS_DIRECTORY)

        if self.check_input(dns_server):
            command.append("-e")
            command.append(dns_server)

        if self.check_input(takeover_check):
            command.append("-t")

        if self.check_input(dns_resolution_virtual_hosts):
            command.append("-v")

        if self.check_input(dns_lookup):
            command.append("-n")

        if self.check_input(dns_bruteforce):
            command.append("-c")

        # TODO incompleto
        if self.check_input(subdomain_resolution):
            command.append("-r")

        # log command
        command_string = ""
        for i in command:
            command_string += i
            command_string += " "

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
            if self.check_input(screenshot):
                data["screenshots_available"] = True
            else:
                data["screenshots_available"] = False

            self.scan_result = data

            # return formatted html
            return self.format_result(data)
        except subprocess.CalledProcessError as e:
            print(e.output.decode("utf-8"))
            print("\033[0m")
            return None

    def format_result(self, scan_result):
        html_output = ""

        if scan_result["screenshots_available"]:
            html_output += (
                "<p>Screenshots saved here: "
                + os.path.abspath(SCREENSHOTS_DIRECTORY)
                + "</p><br>"
            )
            scan_result.pop("screenshots_available")

        html_output += """
                        <table>
                        """

        for key in scan_result.keys():
            html_output += f"""
                <tr>
                    <td><b>{key}</b></td>
                """

            items = ""
            for i in scan_result[key]:
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

    def check_input(self, input):
        return input != None and str(input) != "" and str(input) != "None"
