from zaturn.tools import core


class ZaturnTools:

    def __init__(self, data_sources):
        self.tools = [
            *core.Core(data_sources).tools,
        ]
        

    
