from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from function_schema import get_function_schema
from openai import AsyncOpenAI

from zaturn.tools import ZaturnTools


set_tracing_disabled(disabled=True)
DEFAULT_BASE_URL = 'https://api.openai.com/v1/chat/completions'


class ZaturnAgent:
    
    def __init__(self, state: dict):
        
        self._agent = Agent(
            name = "Zaturn",
            instructions = """
                You are a helpful data analysis assistant.
                Use only the tool provided data sources to process user inputs.
                Do not use external sources or your own knowledge base.
                Also, the tool outputs are shown to the user.
                So, please avoid repeating the tool outputs in the generated text.
                Use list_sources and describe_table whenever needed, 
                do not prompt the user for source names and column names.
            """,
            model = OpenAIChatCompletionsModel(
                model = state['api_model'],
                openai_client = AsyncOpenAI(
                    base_url = state.get('api_endpoint', DEFAULT_BASE_URL),
                    api_key = state.get('api_key'),
                ),
            ),
            tools = list(map(
                function_tool,
                ZaturnTools(state['sources']).tools,
            )),
        )
        

    def get_reply(self, input_list):
        result = Runner.run_sync(self._agent, input_list, max_turns=100)
        print(result)
        print(result.final_output)
        


if __name__=="__main__":
    from zaturn.studio import storage
    state = storage.load_state()
        

    z = ZaturnAgent(state)
    z.get_reply('List Data Sources')
