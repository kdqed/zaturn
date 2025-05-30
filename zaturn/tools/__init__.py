from zaturn.tools import core


class ZaturnTools:

    def __init__(self, data_sources):
        self.tools = [
            *core.Attach(data_sources).tools,
        ]
        

    
