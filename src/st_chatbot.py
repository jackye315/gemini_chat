import streamlit as st
import pandas as pd
import google.generativeai as genai
from typing import Union, List
from oracle_db.oracle_db import create_connection_pool, test_connection, get_table, get_conversation_messages, write_conversation_message, delete_conversation
from genai.gemini_api import get_gemini_model, gemini_chat, gemini_function_call
from agent import youtube_agent, reddit_agent, agent_chat

import os
gemini_api_key = os.environ['gemini_api_key']
oracle_admin_password = os.environ['oracle_admin_password']
oracle_db_dsn = os.environ['oracle_db_dsn']
oracle_cert_path = os.environ['oracle_cert_path']

db_connection_pool = create_connection_pool(
    config_dir=oracle_cert_path,
    user="ADMIN",
    password=oracle_admin_password,
    dsn=oracle_db_dsn,
    wallet_dir=oracle_cert_path,
    wallet_password=oracle_admin_password,
    min=1,
    max=10
)

# def get_gemini_model(model_name:str="gemini-1.5-flash", safety_settings:dict={}, api_key:str=gemini_api_key):
#     genai.configure(api_key=api_key)
#     return genai.GenerativeModel(model_name, safety_settings=safety_settings)

# def gemini_chat(model, query:Union[str, List[str]], chat=None):
#     if not chat:
#         chat = model.start_chat()
#     response = chat.send_message(query)
#     return chat, response.text

def chatbot():
    st.title("Bootleg ChatGPT")

    global db_connection_pool
    if not test_connection(connection=db_connection_pool.acquire()):
        db_connection_pool = create_connection_pool(
            config_dir=oracle_cert_path,
            user="ADMIN",
            password=oracle_admin_password,
            dsn=oracle_db_dsn,
            wallet_dir=oracle_cert_path,
            wallet_password=oracle_admin_password,
            min=1,
            max=10
        )

    # Initialize session state for storing the conversation
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = "gemini-1.5-flash"
        model = get_gemini_model(model_name=st.session_state.gemini_model, api_key=gemini_api_key)
    if 'agent' not in st.session_state:
        st.session_state.agent = "base"
    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = "A"
    if 'previous_conversation' not in st.session_state:
        st.session_state.previous_conversation = ""
    if 'messages' not in st.session_state:
        conversation_df = get_table("MESSAGES", connection=db_connection_pool.acquire())
        curr_conversation_df = conversation_df[conversation_df['CONVERSATION_ID']==st.session_state.current_conversation]
        st.session_state.messages = list(curr_conversation_df['MESSAGE_TEXT'])
    if 'gemini_history' not in st.session_state:
        chat_gemini_history = [{"role":"user", "parts":convo} if index%2==0 else {"role":"model", "parts":convo} for index, convo in enumerate(list(curr_conversation_df['MESSAGE_TEXT']))]
        st.session_state.gemini_history = model.start_chat(history=chat_gemini_history)
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""

    st.write("Conversation " + st.session_state.current_conversation)
    model = get_gemini_model(model_name=st.session_state.gemini_model, api_key=gemini_api_key)
    
    if st.session_state.previous_conversation != st.session_state.current_conversation:
        conversation_df = get_table("MESSAGES", connection=db_connection_pool.acquire())
        curr_conversation_df = conversation_df[conversation_df['CONVERSATION_ID']==st.session_state.current_conversation]
        st.session_state.messages = list(curr_conversation_df['MESSAGE_TEXT'])
        chat_gemini_history = [{"role":"user", "parts":convo} if index%2==0 else {"role":"model", "parts":convo} for index, convo in enumerate(list(curr_conversation_df['MESSAGE_TEXT']))]
        st.session_state.gemini_history = model.start_chat(history=chat_gemini_history)
        st.session_state.previous_conversation = st.session_state.current_conversation
    with st.sidebar:
        # Select model, agent, and conversation
        model_options = ["gemini-1.5-flash", "gemini-1.5-pro"]
        selected_option = st.radio('Gemini Model:', model_options, index=0)
        st.session_state.gemini_model = selected_option
        
        agent_options = ["Base", "Reddit", "Youtube"]
        selected_agent = st.radio('Agent:', agent_options, index=0)
        st.session_state.agent = selected_agent.lower()
        
        if st.button("Conversation A"):
            st.session_state.previous_conversation = st.session_state.current_conversation
            st.session_state.current_conversation = "A"
            st.rerun()
        if st.button("Conversation B"):
            st.session_state.previous_conversation = st.session_state.current_conversation
            st.session_state.current_conversation = "B"
            st.rerun()
        if st.button("Conversation C"):
            st.session_state.previous_conversation = st.session_state.current_conversation
            st.session_state.current_conversation = "C"
            st.rerun()

    # Function to simulate a chatbot response
    def chatbot_response(user_input):
        if st.session_state.agent == 'base':
            st.session_state.gemini_history, chat_response = gemini_chat(model=model, query=user_input, chat=st.session_state.gemini_history)
        elif st.session_state.agent == 'youtube':
            youtube_bot = youtube_agent()
            youtube_model = get_gemini_model(
                    model_name=st.session_state.gemini_model, 
                    api_key=gemini_api_key, 
                    tools=youtube_bot.controls, 
                    system_instruction=youtube_bot.instruction
                )
            st.session_state.gemini_history, chat_response = agent_chat(model=youtube_model, query=user_input, chat=st.session_state.gemini_history, agent=youtube_bot)
        elif st.session_state.agent == 'reddit':
            reddit_bot = reddit_agent()
            reddit_model = get_gemini_model(
                    model_name=st.session_state.gemini_model, 
                    api_key=gemini_api_key, 
                    tools=reddit_bot.controls, 
                    system_instruction=reddit_bot.instruction
                )
            st.session_state.gemini_history, chat_response = agent_chat(model=reddit_model, query=user_input, chat=st.session_state.gemini_history, agent=reddit_bot)
        return chat_response.text
    
    def chatbot_action():
        if user_input:            
            # Append user message to the conversation history
            st.session_state.messages.append(user_input)
            
            # Generate chatbot response and append it to the conversation history
            bot_reply = chatbot_response(user_input)
            st.session_state.messages.append(bot_reply)

            # Write responses to table
            write_conversation_message(table_name="MESSAGES", conversation_id=st.session_state.current_conversation, message_sender="USER", message=user_input,connection=db_connection_pool.acquire())
            write_conversation_message(table_name="MESSAGES", conversation_id=st.session_state.current_conversation, message_sender="BOT", message=bot_reply,connection=db_connection_pool.acquire())

    # Custom CSS for message styling to allow right-align for user
    st.markdown(
        """
    <style>
        .st-emotion-cache-janbn0 {
            flex-direction: row-reverse;
            text-align: right;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Display conversation in a chat-like layout
    for i, message in enumerate(st.session_state.messages):
        role = "user" if i % 2 == 0 else "bot"  # Alternate between user and bot messages
        with st.chat_message(role):
            st.write(message.replace("$", "\$"))
        
    # Clear button
    if st.button("Clear", key="clear_button"):
        st.session_state.messages = []
        st.session_state.gemini_history = None
        delete_conversation(
          table_name="MESSAGES",
          conversation_id=st.session_state.current_conversation,
          connection=db_connection_pool.acquire()
        )
        st.rerun()

    # User input
    st.divider()  # Optional divider for a cleaner separation
    with st.form("input_area", clear_on_submit=True, enter_to_submit=True):
        user_input = st.text_input("You:", key="user_input")
        col1, col2 = st.columns([8,1])
        with col2:
            submit_button = st.form_submit_button("Enter")
        if submit_button:
            chatbot_action()
            st.rerun()
