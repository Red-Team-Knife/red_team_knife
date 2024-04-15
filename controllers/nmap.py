import nmap3


class NmapController:
    def __init__(self):
        self.scan_options = [
            {"top": "Top Ports"},
            {"dns": "DNS Brute Script (Subdomains)"},
            {"list": "List Hosts"},
            {"os": "Detect Os"},
            {"version": "Port Version"},
        ]
        self.last_scan_result = None
        

    

    def run(self, target, type):
        nmap = nmap3.Nmap()

#TODO: salvare tutti i diversi tipi di scansione
        '''
        
        if self.last_scan_result is not None:
     '''       

        if type == "top":
            self.last_scan_result = nmap.scan_top_ports(target)
            return self.format_top_result(self.last_scan_result)
        elif type == "dns":
            self.last_scan_result = nmap.nmap_dns_brute_script(target)
            return self.format_dns_result(self.last_scan_result)
        elif type == "list":
            self.last_scan_result = nmap.nmap_list_scan(target)
            return self.format_list_result(self.last_scan_result)
        elif type == "os":
            self.last_scan_result = nmap.nmap_os_detection(target)
            return self.format_os_result(self.last_scan_result)
        elif type == "version":
            self.last_scan_result = nmap.nmap_version_detection(target)
            return self.format_version_result(self.last_scan_result)
        else:
            return self.format_error()

    def format_list_result(self, scan_result):
        html_output = """
                        <table>
                            <tr>
                                <th>Ip</th>
                                <th>Hostname</th>
                                <th>Type</th>
                            </tr>
                        """

        ips = scan_result.keys() - ["runtime", "stats", "task_results"]

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

    def format_os_result(self, scan_result):
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
        ips = scan_result.keys() - ["runtime", "stats", "task_results"]
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

    def format_version_result(self, scan_result):
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

    def format_dns_result(self, scan_result):
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

    def format_top_result(self, scan_result):
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
                    </tr>
                
                """
        html_output += "</table>"
        return html_output
