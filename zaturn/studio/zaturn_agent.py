import asyncio
import json

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from function_schema import get_function_schema
from openai import AsyncOpenAI
import httpx

from zaturn.tools import ZaturnTools


set_tracing_disabled(disabled=True)
DEFAULT_BASE_URL = 'https://api.openai.com/v1'


class ZaturnAgent:
    
    def __init__(self, state: dict):
        self._state = state
        sources = {} 
        for s in state['sources']:
            if state['sources'][s]['active']:
                sources[s] = state['sources'][s]
                
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
                ZaturnTools(sources).tools,
            )),
        )
        

    async def run_async(self, input_list):
        result = await Runner.run(self._agent, input_list, max_turns=100)
        return result.to_input_list()
    
    def run(self, question):
        state = self._state
        r = httpx.post(
            url = f'{state["api_endpoint"]}/chat/completions',
            headers = {
                'Authorization': f'Bearer {state["api_key"]}'
            },
            json = {
                'model': state["api_model"],
                'messages': [{
                    'role': 'user',
                    'content': question,
                }],
            }
        )

        response = r.json()
        print(response['usage'])
        return [response['choices'][0]['message']]

if __name__=="__main__":
    from zaturn.studio import storage
    state = storage.load_state()
        

    z = ZaturnAgent(state)
    print(z.run('Hello'))
