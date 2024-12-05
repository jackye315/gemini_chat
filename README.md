Building a simple streamlit chatbot. Adding authentication for added security. Integrates with Oracle Autonomous Database for persistant chats and Gemini API for chat generation. Also easy to deploy with Docker and nginx containers for reverse proxy.

## "Agents"
Currently support searching Reddit and Youtube. In both these cases, I use Gemini Function Calls to call each API and then feed the output to Gemini to process.
- Reddit: Utilize Google Search API to find links on Reddit. Then use PRAW Python Reddit API to scrape each Reddit link.
- Youtube: Utilize Google Youtube API to find links on Youtube. Then use third party [Youtube-Transcript-API](https://github.com/jdepoix/youtube-transcript-api) to obtain the transcripts from each video.

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