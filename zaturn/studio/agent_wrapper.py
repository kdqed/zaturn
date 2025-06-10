import asyncio
import json

from function_schema import get_function_schema
import httpx


class Agent:

    def __init__(self, 
        endpoint: str,
        api_key: str,
        model: str,
        tools: list = [],
    ):
    
        self._post_url = f'{endpoint}/chat/completions'
        self._api_key = api_key
        self._model = model
        self._system_message = {
            'role': 'system',
            'content': """
                You are a helpful data analysis assistant.
                Use only the tool provided data sources to process user inputs.
                Do not use external sources or your own knowledge base.
                Also, the tool outputs are shown to the user.
                So, please avoid repeating the tool outputs in the generated text.
                Use list_sources and describe_table whenever needed, 
                do not prompt the user for source names and column names.
            """,
        }
        
        self._tools = []
        self._tool_map = {}
        for tool in tools:
            tool_schema = get_function_schema(tool)
            self._tools.append({
                'type': 'function', 
                'function': tool_schema,
            })
            self._tool_map[tool_schema['name']] = tool
        
    
    def run(self, messages):
        if type(messages) is str:
            messages = [{'role': 'user', 'content': messages}]

        while True:
            res = httpx.post(
                url = self._post_url,
                headers = {
                    'Authorization': f'Bearer {self._api_key}'
                },
                json = {
                    'model': self._model,
                    'messages': [self._system_message] + messages,
                    'tools': self._tools,
                    'reasoning': {'exclude': True},
                }
            )

            resj = res.json()
            reply = resj['choices'][0]['message']
            messages.append(reply)

            tool_calls = reply.get('tool_calls')
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    tool_response = self._tool_map[tool_name](**tool_args)
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call['id'],
                        'name': tool_name,
                        'content': json.dumps(tool_response)
                    })
            else:
                break

        return messages

    
