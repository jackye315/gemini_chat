import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def google_search(search_query:str, api_key:str, engine_id_cx:str, **kwargs):
    
    params = {
        "q": search_query,
        "key": api_key,
        "cx": engine_id_cx,
    }

    if "date_filter" in kwargs:
        params["dateRestrict"] = kwargs["date_filter"]
    if "num_results" in kwargs:
        params["num"] = kwargs["num_results"]
    if "country_code" in kwargs:
        params["gl"] = kwargs["country_code"]

    uri="https://www.googleapis.com/customsearch/v1"
    response = requests.get(uri, params=params)
    return response.json()

def clean_search_output(google_results):
    output = []
    for item in google_results['items']:
        output_dict = {}
        output_dict['link'] = item['link']
        output_dict['title'] = item['title']
        output_dict['snippet'] = item['snippet']
        output.append(output_dict)
    return output

if __name__=="__main__":
    import os
    google_api_key = os.environ['google_api_key']
    reddit_engine_id_cx = os.environ['google_reddit_engine_id_cx']
    full_engine_id_cx = os.environ['google_all_engine_id_cx']

    search_query = "nfl week 11 results"
    results = google_search(search_query=search_query, api_key=google_api_key, engine_id_cx=reddit_engine_id_cx, num_results=5)
    output_list = clean_search_output(results)
    output_list