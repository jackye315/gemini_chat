import requests
import os
from dotenv import load_dotenv
load_dotenv()
google_api_key = os.environ['google_api_key']

from typing import Union, List

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

def _base_youtube_api(
        url:str,
        return_parts:str,
        api_key:str=google_api_key, 
        **kwargs
    ):
    
    params = {
        "part":return_parts,
        "type":"video",
        "key": api_key,
    }

    if "search_query" in kwargs:
        params["q"] = kwargs["search_query"]
    if "video_id" in kwargs:
        params["id"] = kwargs["video_id"]
    if "date_filter" in kwargs:
        params["dateRestrict"] = kwargs["date_filter"]
    if "max_results" in kwargs:
        params["maxResults"] = kwargs["max_results"]

    return requests.get(url, params=params)

def youtube_search_api(
        search_query:str, 
        max_results: int = 5,
        url:str = "https://www.googleapis.com/youtube/v3/search",
        return_parts:str= "snippet",
        **kwargs
    ):
    
    return _base_youtube_api(url=url, return_parts=return_parts, search_query=search_query, max_results=max_results, kwargs=kwargs)

def youtube_video_api(
        video_id:Union[str, List[str]],
        url:str = "https://www.googleapis.com/youtube/v3/videos",
        return_parts:str="statistics",
        **kwargs
    ):
    return _base_youtube_api(url=url, return_parts=return_parts, video_id=video_id, kwargs=kwargs)

def url_to_id(youtube_link:str):
    if "shorts" in youtube_link:
        return youtube_link.split('/')[-1]
    else:
        return youtube_link.split("=")[-1]

def get_transcript(video_id:str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        transcript = [{'text':""}]
    return transcript

def get_full_transcript(transcript):
    full_transcript = ""
    for part in transcript:
        full_transcript = full_transcript + part['text']
    return full_transcript

def get_full_youtube_data(search_query:str, max_search_results:int = 5):
    response = youtube_search_api(search_query=search_query, max_results=max_search_results)
    response.json()
    results_list = []
    results = response.json()['items']
    for result in results:
        results_dict = {}
        results_dict['video_id'] = result['id']['videoId']
        results_dict['title'] = result['snippet']['title']
        results_dict['channel'] = result['snippet']['channelTitle']
        results_dict['upload_time'] = result['snippet']['publishedAt']
        video_results = youtube_video_api(video_id=results_dict['video_id']).json()['items']
        results_dict['view_count'] = video_results[0]['statistics']['viewCount']
        results_dict['like_count'] = video_results[0]['statistics']['likeCount']
        results_dict['comment_count'] = video_results[0]['statistics']['commentCount']

        transcript = get_transcript(results_dict['video_id'])
        results_dict['transcript'] = get_full_transcript(transcript=transcript)
        results_list.append(results_dict)
    return results_list

if __name__=="__main__":
    from gemini_api import get_gemini_model, gemini_call, gemini_chat
    gemini_model = get_gemini_model()

    # Single video given youtube link
    video_link = "https://www.youtube.com/watch?v=oNO6CJ6GseE"
    video_id = url_to_id(youtube_link=video_link)
    transcript = get_transcript(video_id)
    full_transcript = get_full_transcript(transcript)

    question = "Given this information, what unit should I buff?"
    # chat, response = gemini_chat(model=gemini_model, chat=None, query=[full_transcript, question])
    print(gemini_call(gemini_model,[full_transcript,question]))

    # # Youtube Search return multiple videos
    # topic = "best linen pants men"
    # results_list = get_full_youtube_data(search_query=topic, max_search_results=10)
    # question = "Given this information, what are the best linen pant brands for the money?"
    # print(gemini_call(gemini_model,[*[result['transcript'] for result in results_list],question]))