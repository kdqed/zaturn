import asyncio
import json

from function_schema import get_function_schema
import httpx
from mcp.types import ImageContent
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_core import to_jsonable_python


class ZaturnAgent:

    def __init__(self, 
        endpoint: str,
        api_key: str,
        model_name: str,
        tools: list = [],
        image_input: bool = False,
        reasoning_effort: str = 'none',
        system_prompt: str = '',
    ):
    
        model_settings = None
        reasoning_effort = reasoning_effort.lower()
        if reasoning_effort in ['low', 'medium', 'high']:
            model_settings = OpenAIChatModelSettings(
                openai_reasoning_effort = reasoning_effort,
            )
            
        self._agent = Agent(
            OpenAIChatModel(
                model_name,
                provider = OpenAIProvider(
                    api_key = api_key,
                    base_url = endpoint,
                )
            ),
            model_settings = model_settings,
            system_prompt = system_prompt or None,
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
    
