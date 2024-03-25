import nmap3
import json

class NmapController():
    def __init__(self):
        self.scan_in_progress = False

    def scan(self, target, type):
        self.scan_in_progress = True

        nmap = nmap3.Nmap()

        if type == 'top':
            nm_scan = nmap.scan_top_ports(target)
            self.scan_in_progress = False
            return self.format_top_result(nm_scan)
        elif type == 'dns':
            nm_scan = nmap.nmap_dns_brute_script(target)
            self.scan_in_progress = False
            return self.format_dns_result(nm_scan)
        elif type == 'list':
            nm_scan = nmap.nmap_list_scan(target)
            self.scan_in_progress = False
            return self.format_list_result(nm_scan)
        elif type == 'os':
            nm_scan = nmap.nmap_os_detection(target)
            self.scan_in_progress = False
            return self.format_os_result(nm_scan)
        elif type == 'subnet':
            nm_scan = nmap.nmap_subnet_scan(target)
            self.scan_in_progress = False
            return self.format_subnet_result(nm_scan)
        elif type == 'version':
            nm_scan = nmap.nmap_version_detection(target)
            self.scan_in_progress = False
            return self.format_version_result(nm_scan)
        else:
            return self.format_error()

#TODO verificare la presenza dei campi. se non presenti lasciare spazio vuoto
        
    def format_list_result(self, scan_result):
        html_output =   """
                        <table>
                            <tr>
                                <th>Ip</th>
                                <th>Hostname</th>
                                <th>Type</th>
                            </tr>
                        """

        ips = scan_result.keys() - ['runtime', 'stats', 'task_results']
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for hostname in scan_result[ip]['hostname']:
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
        html_output =   """
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
        ips = scan_result.keys() - ['runtime', 'stats', 'task_results']
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for os_info in scan_result[ip]['osmatch']:
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

#TODO non funziona
    def format_subnet_result(self, scan_result):
        print(scan_result)

    def format_version_result(self, scan_result):
        print(scan_result)
        html_output =   """
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

        ips = scan_result.keys() - ['runtime', 'stats', 'task_results']
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]['ports']:
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
        html_output =   """
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
        html_output =   """
                        <table>
                            <tr>
                                <th>Hostname</th>
                                <th>Port</th>
                                <th>Protocol</th>
                                <th>Status</th>
                                <th>Service</th>
                            </tr>
                        """

        ips = scan_result.keys() - ['runtime', 'stats', 'task_results']
        # Loop through each IP address
        for ip in ips:
            print(ip)
            for port_info in scan_result[ip]['ports']:
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