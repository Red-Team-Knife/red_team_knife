import nmap3

def scan(target, options):
    #TODO eseguire scansione con diverse opzioni
    nm = nmap3.Nmap()
    nm_scan = nm.scan_top_ports(target, args=options)
    
    return format_result(nm_scan)

def format_result(scan_result):
    #TODO completare formattazione
    return scan_result