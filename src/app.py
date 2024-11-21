import streamlit as st
import streamlit_authenticator as stauth
from st_chatbot import chatbot

import yaml
from yaml.loader import SafeLoader
import os
auth_config_path = os.environ['auth_config_path']

with open(f'{auth_config_path}/auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

if __name__=="__main__":
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state['authentication_status']:
        authenticator.logout()
        chatbot_page = st.Page(chatbot, title="Chatbot", icon=":material/smart_toy:")
        pg = st.navigation(
            {
                "Chat":[chatbot_page],
            }
        )
        pg.run()
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')