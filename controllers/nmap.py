import nmap3
from controllers.controller import Controller

scan_options = [
    ("Top Ports", "radio", "top", "type"),
    ("DNS Brute Script (Subdomains)", "radio", "dns", "type"),
    ("List Hosts", "radio", "list", "type"),
    ("Detect Os", "radio", "os", "type"),
    ("Port Version", "radio", "version", "type"),
]

class NmapController(Controller):
    def __init__(self):       
        self.last_scan_result = None

    def run(self, target, options):
        nmap = nmap3.Nmap()
        print(options)

        type = options['type']
        
        if type == "top":
            self.last_scan_result = nmap.scan_top_ports(target)
            html = self.__format_top_result__(self.last_scan_result)
        elif type == "dns":
            self.last_scan_result = nmap.nmap_dns_brute_script(target)
            html = self.__format_dns_result__(self.last_scan_result)
        elif type == "list":
            self.last_scan_result = nmap.nmap_list_scan(target)
            html = self.__format_list_result__(self.last_scan_result)
        elif type == "os":
            self.last_scan_result = nmap.nmap_os_detection(target)
            html = self.__format_os_result__(self.last_scan_result)
        elif type == "version":
            self.last_scan_result = nmap.nmap_version_detection(target)
            
            html = self.__format_version_result__(self.last_scan_result)
        else:
            html = self.format_error()
        self.last_scan_result["type"] = type
        
        return html

    def restore_last_scan(self):
        type = self.last_scan_result['type']
        if type == "top":
            return self.__format_top_result__(self.last_scan_result)
        elif type == "dns":
            return self.__format_dns_result__(self.last_scan_result)
        elif type == "list":
            return self.__format_list_result__(self.last_scan_result)
        elif type == "os":
            return self.__format_os_result__(self.last_scan_result)
        elif type == "version":
            return self.__format_version_result__(self.last_scan_result)
        else:
            return self.format_error()

    def __format_list_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Ip</th>
                                <th>Hostname</th>
                                <th>Type</th>
                            </tr>
                        """

        ips = self.__remove_unnecessary_keys__(scan_result.keys())
        print('ips', ips)

        # Loop through each IP address
        for ip in ips:
            print(ip)
            for hostname in scan_result[ip]["hostname"]:
                html_output += f"""
                    <tr>
                        <td>{ip}</td>
                        <td>{hostname['name']}</td>
                        <td>{hostname['type']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_os_result__(self, scan_result):
        print(scan_result)
        html_output = """
                        <table>
                            <tr>
                                <th>Address</th>
                                <th>Os match</th>
                                <th>Line</th>
                                <th>Accuracy</th>
                                <th>Os family</th>
                                <th>Type</th>
                                <th>Vendor</th>
                            </tr>
                        """
        ips = scan_result.keys() - ["runtime", "stats", "task_results", "type"]
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for os_info in scan_result[ip]["osmatch"]:
                html_output += f"""
                    <tr>
                        <td>{ip}</td>
                        <td>{os_info['name']}</td>
                        <td>{os_info['line']}</td>
                        <td>{os_info['osclass']['accuracy']}</td>
                        <td>{os_info['osclass']['osfamily']}</td>
                        <td>{os_info['osclass']['type']}</td>
                        <td>{os_info['osclass']['vendor']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_version_result__(self, scan_result):
        print(scan_result)
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Port</th>
                                <th>Protocol</th>
                                <th>Status</th>
                                <th>Service Name</th>
                                <th>Conf</th>
                                <th>Extra info</th>
                                <th>Method</th>
                                <th>Os type</th>
                                <th>Product</th>
                                <th>Tunnel</th>
                                <th>Version</th>
                            </tr>
                        """

        ips = scan_result.keys() - ["runtime", "stats", "task_results"]
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]["ports"]:
                html_output += f"""
                    <tr class="{'' if port_info['state'] != 'open' else 'open'}">
                        <td>{', '.join(host['name'] for host in scan_result[ip]['hostname'])}</td>
                        <td>{port_info['portid']}</td>
                        <td>{port_info['protocol']}</td>
                        <td>{port_info['state']}</td>
                        <td>{port_info['service']['name']}</td>
                        <td>{port_info['service'].get('conf', '')}</td>
                        <td>{port_info['service'].get('extrainfo', '')}</td>
                        <td>{port_info['service'].get('method', '')}</td>
                        <td>{port_info['service'].get('ostype', '')}</td>
                        <td>{port_info['service'].get('product', '')}</td>
                        <td>{port_info['service'].get('tunnel', '')}</td>
                        <td>{port_info['service'].get('version', '')}</td>

                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __format_dns_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Address</th>
                            </tr>
                        """

        for address in scan_result:
            html_output += f"""
                <tr>
                    <td>{address['hostname']}</td>
                    <td>{address['address']}</td>
                </tr>
            
                """
        html_output += "</table>"
        return html_output

    def __format_top_result__(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Port</th>
                                <th>Protocol</th>
                                <th>Status</th>
                                <th>Service</th>
                            </tr>
                        """

        ips = self.__remove_unnecessary_keys__(scan_result.keys())
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]["ports"]:
                html_output += f"""
                    <tr class="{'' if port_info['state'] != 'open' else 'open'}">
                        <td>{', '.join(host['name'] for host in scan_result[ip]['hostname'])}</td>
                        <td>{port_info['portid']}</td>
                        <td>{port_info['protocol']}</td>
                        <td>{port_info['state']}</td>
                        <td>{port_info['service']['name']}</td>
                    </tr>
                
                """
        html_output += "</table>"
        return html_output

    def __remove_unnecessary_keys__(self, keys):
        return keys - ["runtime", "stats", "task_results", "type"]