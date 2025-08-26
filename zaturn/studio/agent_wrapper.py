import asyncio
import json

from function_schema import get_function_schema
import httpx
from mcp.types import ImageContent
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_core import to_jsonable_python


class ZaturnAgent:

    def __init__(self, 
        endpoint: str,
        api_key: str,
        model_name: str,
        tools: list = [],
        image_input: bool = False,
    ):
    
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

        self._agent = Agent(
            OpenAIModel(
                model_name,
                provider = OpenAIProvider(
                    api_key = api_key,
                    base_url = endpoint,
                )
            ),
            system_prompt = self._system_message['content'],
            tools = tools,
        )
        


    def run(self, prompt, message_history = None):
        if message_history:
            message_history_obj = ModelMessagesTypeAdapter.validate_python(message_history)
            result = self._agent.run_sync(prompt, message_history = message_history_obj)
            return to_jsonable_python(result.all_messages())
        else:
            result = self._agent.run_sync(prompt)
            return to_jsonable_python(result.all_messages())
    
