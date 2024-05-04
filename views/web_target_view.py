from current_scan import CurrentScan
from views.view import BaseBlueprint


class WebTargetBlueprint(BaseBlueprint):
    def __build_target__(self):
        return CurrentScan.scan.protocol + '://' + CurrentScan.scan.host + CurrentScan.scan.resource