import asyncio
import json

from function_schema import get_function_schema
import httpx
from mcp.types import ImageContent


class Agent:

    def __init__(self, 
        endpoint: str,
        api_key: str,
        model: str,
        tools: list = [],
        image_input: bool = False,
    ):
    
        self._post_url = f'{endpoint}/chat/completions'
        self._api_key = api_key
        self._model = model
        self._image_input = image_input
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


    def _prepare_input_messages(self, messages):
        input_messages = [self._system_message]
        for message in messages:
            if message['role']!='tool':
                input_messages.append(message)
            elif type(message['content']) is not list:
                input_messages.append(message)
            else:
                new_content = []
                image_content = None
                for content in message['content']:
                    if content['type']=='image_url':
                        image_content = content
                        new_content.append({
                            'type': 'text',
                            'text': 'Tool call returned an image to the user.',
                        })
                    else:
                        new_content.append(content)
                input_messages.append({
                    'role': message['role'],
                    'tool_call_id': message['tool_call_id'],
                    'name': message['name'],
                    'content': new_content,
                })

        return input_messages                
        
    
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
                    'messages': self._prepare_input_messages(messages),
                    'tools': self._tools,
                    'reasoning': {'exclude': True},
                }
            )

            print(res.text)
            resj = res.json()
            reply = resj['choices'][0]['message']
            messages.append(reply)

            tool_calls = reply.get('tool_calls')
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    tool_response = self._tool_map[tool_name](**tool_args)
                    if type(tool_response) is ImageContent:
                        b64_data = tool_response.data
                        data_url = f'data:image/png;base64,{b64_data}'
                        content = [{
                            'type': 'image_url',
                            'image_url': {
                                "url": data_url,
                            }                            
                        }]
                    else:
                        content = [{
                            'type': 'text',
                            'text': json.dumps(tool_response)
                        }]
                        
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call['id'],
                        'name': tool_name,
                        'content': content
                    })
            else:
                break

        return messages

    
