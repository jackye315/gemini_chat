Building a simple streamlit chatbot. Adding authentication for added security. Integrates with Oracle Autonomous Database for persistant chats and Gemini API for chat generation. Also easy to deploy with Docker and nginx containers for reverse proxy.

## Getting Started
1. Create .env from sample.env
2. Create nginx.conf from nginx-template.conf
3. Create auth_config.yaml from auth_config_template.yaml. To check documentation, visit [Streamlit-Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)

## How to Run
Directly running streamlit:
```console
streamlit run app.py
```

Through Docker:
```console
make up
```