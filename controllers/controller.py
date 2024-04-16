class Controller():
    def __init__(self):
        self.last_scan_result = None
    
    def run(self, target, options):
        pass
    
    def restore_last_scan(self):
        return self.__format_result__()
    
    def __format_result__(self):
        pass