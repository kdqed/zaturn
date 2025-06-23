from zaturn.tools import core, visualizations


class ZaturnTools:

    def __init__(self, data_sources):
        self.tools = [
            *core.Core(data_sources).tools,
            *visualizations.Visualizations(data_sources).tools,
        ]
        

    
