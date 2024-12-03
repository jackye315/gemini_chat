import ast
import os
gemini_api_key = os.environ['gemini_api_key']

from typing import Union, List
import google.generativeai as genai

def get_gemini_model(model_name:str="gemini-1.5-flash", tools=None, system_instruction=None, safety_settings:dict={}, api_key:str=gemini_api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name, tools=tools, system_instruction=system_instruction, safety_settings=safety_settings)

def get_safety_off_gemini_model():
    safety_settings=[
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
    return get_gemini_model(safety_settings=safety_settings)

def gemini_call(model, query:Union[str, List[str]]):
    response = model.generate_content(query)
    return response.text

def gemini_chat(model, query:Union[str, List[str]], chat=None):
    if not chat:
        chat = model.start_chat()
    elif chat.model != model:
        chat = genai.ChatSession(model=model, history=chat.history)
    response = chat.send_message(query)
    return chat, response

def gemini_chat_rewind(chat):
    chat.rewind()

def gemini_upload_image(img_name:str):
    return genai.upload_file(img_name)

def gemini_local_upload(download_path:str):
    genai_files_dict = {genai.display_name:genai for genai in get_genai_list()}
    for filename in os.listdir(download_path):
        file_path = os.path.join(download_path, filename)
        if filename not in genai_files_dict:
            genai_files_dict[filename] = gemini_upload_image(file_path)
    return genai_files_dict

def get_genai_list():
    return list(genai.list_files())

def delete_genai_list():
    for f in genai.list_files():
        f.delete()

def gemini_function_call(input, current_chat, possible_functions:dict):
    while input.parts[0].function_call:
        func_results = {}
        for part in input.parts:
            if part.function_call:
                func_name = part.function_call.name
                try:
                    func_args = {key:ast.literal_eval(val) for key, val in part.function_call.args.items()}
                except:
                    func_args = {key:val for key, val in part.function_call.args.items()}
                temp_func = possible_functions[func_name]
                func_results[func_name] = temp_func(**func_args)
        func_results_gemini = [f"Here are the results from the function call\n\nfunction_name: {fn}, function_result: {val}" for fn, val in func_results.items()]
        input = current_chat.send_message(func_results_gemini)
    return input

if __name__=="__main__":
    models = ["gemini-1.5-pro","gemini-1.5-flash"]
    model = get_gemini_model(model_name=models[1],api_key=gemini_api_key)
    question = "What is capital of France?"
    print(gemini_call(model=model, query=question))

    chat, response = gemini_chat(model=model, query="hi")


    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    sys.path.append(parent_dir)
    from agent import youtube_agent
    youtube_bot = youtube_agent()
    model = get_gemini_model(tools=youtube_bot.controls, system_instruction=youtube_bot.instruction)
    gemini_chat(model=model, chat=chat, query="What can you do?")