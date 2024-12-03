import ast
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_utils.youtube import url_to_id, get_transcript_with_timestamps, get_full_transcript, search_full_youtube_data
from genai.gemini_api import get_gemini_model, gemini_chat, gemini_function_call
from typing import Iterable

from google.generativeai.types import content_types

def tool_config_from_mode(mode: str, fns: Iterable[str] = ()):
    """Create a tool config with the specified function calling mode."""
    return content_types.to_tool_config(
        {"function_calling_config": {"mode": mode, "allowed_function_names": fns}}
    )

class youtube_agent:
    def __init__(self):
        self.instruction = (
            """You are a helpful Youtube bot. 
            You can get the transcript from Youtube videos. 
            You can also search Youtube for videos and provide real time results and metadata.
            If you are not provided with a video id, then call the search_full_youtube_data function and search youtube for the question asked.
            Always use this proxy url for the functions get_transcript_with_timestamps, get_full_transcript, and search_full_youtube_data: http://warp:1080. 
            Only answer questions with information from the video transcript or youtube search results. Do not perform any other tasks."""
        )
        self.controls = [url_to_id, get_transcript_with_timestamps, get_full_transcript, search_full_youtube_data]
        self.controls_dict = {f"{function.__name__}":function for function in self.controls}

def agent_chat(model, chat, agent, query: str):
    chat, response = gemini_chat(model=model, chat=chat, query=query)
    if response.parts[0].function_call:
        response = gemini_function_call(input=response, current_chat=chat, possible_functions=agent.controls_dict)
    chat, response = gemini_chat(model=model, chat=chat, query=f"Using all this information, answer the original question. If you already answered the question above, just answer it fully again.\nQuestion: {query}")
    return chat, response

if __name__=="__main__":
    
    youtube_bot = youtube_agent()
    model = get_gemini_model(tools=youtube_bot.controls, system_instruction=youtube_bot.instruction)
    # chat = model.start_chat()
    # tool_config = tool_config_from_mode("none")
    # response = chat.send_message("What can you do?", tool_config=tool_config)
    # print(response.parts[0])

    # tool_config = tool_config_from_mode("any")
    # response = chat.send_message("Get me the full transcript of this video: https://www.youtube.com/watch?v=N4cdKkjbdtE", tool_config=tool_config)
    # response = gemini_function_call(input=response, current_chat=chat, possible_functions=youtube_bot.controls_dict)
    # response = chat.send_message("What is happening here?")
    # response.parts[0]
    
    chat, response = gemini_chat(model=model, query="What can you do?")
    chat, response = agent_chat(model=model, chat=chat, agent=youtube_bot, query="how to setup sunshine")
    response.parts[0]

    # Test response for consistent output
    # import time
    # responses = []
    # for i in range(10):
    #     youtube_bot = youtube_agent()
    #     model = get_gemini_model(tools=youtube_bot.controls, system_instruction=youtube_bot.instruction)
    #     chat, response = gemini_chat(model=model, query="What can you do?")
    #     chat, response = agent_chat(model=model, chat=chat, agent=youtube_bot, query="how to setup sunshine")
    #     responses.append(response.parts[0])
    #     time.sleep(30)