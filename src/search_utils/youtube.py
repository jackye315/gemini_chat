import requests
import os
google_api_key = os.environ['google_api_key']

from typing import Union

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from pydantic import BaseModel

class Transcript(BaseModel):
    text: str
    start: float
    duration: float

class VideoResult(BaseModel):
    video_id: str
    title: str
    channel: str
    upload_time: str
    view_count: str
    like_count: str
    comment_count: str
    transcript: str

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
        video_id:Union[str, list[str]],
        url:str = "https://www.googleapis.com/youtube/v3/videos",
        return_parts:str="statistics",
        **kwargs
    ):
    return _base_youtube_api(url=url, return_parts=return_parts, video_id=video_id, kwargs=kwargs)

def url_to_id(youtube_link:str):
    """Extract the video id from a provided youtube link."""
    if "shorts" in youtube_link:
        return youtube_link.split('/')[-1]
    else:
        return youtube_link.split("=")[-1]

def get_transcript_with_timestamps(video_id:str, proxy_url:str="http://warp:1080") -> list[Transcript]:
    """Get the video transcript with time stamps from the provided youtube video id. If provided, use the proxy url to proxy the api call."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies={'http': proxy_url, 'https': proxy_url})
    except:
        transcript = [{'text':""}]
    
    return transcript

def get_full_transcript(video_id:str, proxy_url:str="http://warp:1080") -> str:
    """Extract the full transcript as a string from the provided youtube video id. If provided, use the proxy url to proxy the api call."""
    transcript = get_transcript_with_timestamps(video_id=video_id, proxy_url=proxy_url)
    full_transcript = ""
    for part in transcript:
        full_transcript = full_transcript + part['text']
    return full_transcript

def search_full_youtube_data(search_query:str, max_search_results:int = 5, proxy_url:str="http://warp:1080") -> list[VideoResult]:
    """Search Youtube and provide real time video results based on the search query. If provided, use the proxy url to proxy the api call.
    Extract the following information for each video:
        video id, title, video channel name, upload time, view count, likes count, comment count, and full video transcript
    
    Arguments:
        search_query: String of the topic to search youtube for using the Google Youtube search API
        max_search_results: Number of results to return. If none provided, default to 5
        proxy_url: String of the proxy url to use when calling the API from if provided
    """
    response = youtube_search_api(search_query=search_query, max_results=int(max_search_results))
    response.json()
    results_list = []
    results = response.json()['items']
    for result in results:
        results_dict = {}
        results_dict['video_id'] = result['id']['videoId']
        results_dict['link'] = f"https://www.youtube.com/watch?v={results_dict['video_id']}"
        results_dict['title'] = result['snippet']['title']
        results_dict['channel'] = result['snippet']['channelTitle']
        results_dict['upload_time'] = result['snippet']['publishedAt']
        video_results = youtube_video_api(video_id=results_dict['video_id']).json()['items']
        results_dict['view_count'] = video_results[0]['statistics']['viewCount']
        results_dict['like_count'] = video_results[0]['statistics']['likeCount']
        results_dict['comment_count'] = video_results[0]['statistics']['commentCount']

        results_dict['transcript'] = get_full_transcript(video_id=results_dict['video_id'], proxy_url=proxy_url)
        results_list.append(results_dict)
    return results_list

if __name__=="__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from genai.gemini_api import get_gemini_model, gemini_call
    gemini_model = get_gemini_model()

    # Single video given youtube link
    video_link = "https://www.youtube.com/watch?v=Jm8KiTUhzNQ"
    video_id = url_to_id(youtube_link=video_link)
    full_transcript = get_full_transcript(video_id=video_id,proxy_url="http://warp:1080")

    question = "Given this information, describe and summarize this video"
    print(gemini_call(gemini_model,[full_transcript,question]))

    # Youtube Search return multiple videos
    topic = "best linen pants men"
    results_list = search_full_youtube_data(search_query=topic, max_search_results=10, proxy_url="http://warp:1080")
    question = "Given this information, what are the best linen pant brands for the money?"
    print(gemini_call(gemini_model,[*[result['transcript'] for result in results_list],question]))