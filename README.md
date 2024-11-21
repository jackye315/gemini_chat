Building a simple streamlit chatbot. Integrates with Oracle Autonomous Database for persistant chats and Gemini API for chat generation. Also easy to deploy with Docker and nginx containers for reverse proxy.

## Getting Started
1. Create .env from sample.env
2. Create nginx.conf from nginx-template.conf

## How to Run
Directly running streamlit:
```console
streamlit run app.py
```

Through Docker:
```
make up
```