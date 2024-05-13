import tldextract
from current_scan import CurrentScan
from views.view import BaseBlueprint

def get_domain_name(url):
    extracted = tldextract.extract(url)
    return extracted.domain + '.' + extracted.suffix


class DomainNameTargetBlueprint(BaseBlueprint):
    def __build_target__(self):
        return get_domain_name(CurrentScan.scan.host)