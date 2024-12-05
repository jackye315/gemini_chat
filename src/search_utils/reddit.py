from datetime import datetime
import praw
import os
reddit_user = os.environ['user']
reddit_client_id = os.environ['reddit_client_id']
reddit_client_secret = os.environ['reddit_client_secret']
google_api_key = os.environ['google_api_key']
reddit_engine_id_cx = os.environ['google_reddit_engine_id_cx']
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_utils.google import google_search, clean_search_output

from pydantic import BaseModel

def reddit_setup(client_id, client_secret, user,):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost",
        user_agent=f"{user}_scrape_post by u/{user}",
    )
    return reddit

def get_post_data(submission) -> dict:
    post_data = {}
    post_data['author'] = submission.author
    post_data['title'] = submission.title
    post_data['post_date'] = str(datetime.fromtimestamp(submission.created_utc))
    post_data['score'] = submission.score
    post_data['link'] = submission.url
    post_data['body_text'] = submission.selftext
    return post_data

def _create_comment_dict(submission) -> dict:
    comments_dict = {}
    for comment in submission.comments.list():
        comments_dict[comment.id] = comment
    return comments_dict

def create_comment_conversations(submission) -> list:
    comments_dict = _create_comment_dict(submission)
    
    seen_comments = {}
    comment_conversations = []
    for comment in reversed(submission.comments.list()):
        if comment.id not in seen_comments:
            seen_comments[comment.id] = comment
            curr_comment = comment
            conversation = [curr_comment]
            while curr_comment.parent_id.split('_')[-1] != submission.id:
                curr_comment = comments_dict[curr_comment.parent_id.split('_')[-1]]
                seen_comments[curr_comment.id] = curr_comment
                conversation.append(curr_comment)
            comment_conversations.append(list(reversed(conversation)))
    return comment_conversations

def sort_comment_conversations(comment_order_dict, comment_conversations):
    sorted_conversations = sorted(comment_conversations, key=lambda x: [comment_order_dict[item] for item in x])
    return sorted_conversations

def get_post_and_comments(reddit, url:str):
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=None)
    post_data = get_post_data(submission)
    comment_conversations = create_comment_conversations(submission)

    ordered_comments = {key:index for index, key in enumerate(submission.comments.list())}
    sorted_conversations = sort_comment_conversations(ordered_comments, comment_conversations=comment_conversations)
    conversations_list = []
    for conversation in sorted_conversations:
        comments_list = []
        for comment in conversation:
            temp_conversation = {}
            temp_conversation['user'] = comment.author
            temp_conversation['comment_date'] = str(datetime.fromtimestamp(comment.created_utc))
            temp_conversation['score'] = comment.score
            temp_conversation['text'] = comment.body
            comments_list.append(temp_conversation)
        conversations_list.append(comments_list)
    post_data['conversations'] = conversations_list
    return post_data

class RedditComments(BaseModel):
    user: str
    comment_date: str
    score: int
    text: str

class RedditConversations(BaseModel):
    comments: list[RedditComments]

class RedditPost(BaseModel):
    author: str
    title: str
    post_date: str
    score: int
    link: str
    body_text: str
    conversations: list[RedditConversations]

def search_reddit(
        search_query:str, 
        reddit_client_id:str=reddit_client_id, 
        reddit_client_secret:str=reddit_client_secret, 
        reddit_user:str=reddit_user,
        google_api_key:str=google_api_key,
        reddit_engine_id_cx:str=reddit_engine_id_cx,
    ) -> list[RedditPost]:
    """Search Reddit for the search_query topic and return a list of relevant posts and the corresponding comments.
    Search by using the below steps:
        1. Perform a Google Search with the provided Reddit Search Engine to return 5 Reddit links according to Google
        2. Use Reddit PRAW API to extract the post and comments in each link
            In each Post, extract the Author, Title, Date of Post, Up/Down Score, Link, and Text
            In each Comment, extract the User, Date of Comment, Up/Down Score, and Text
                Note: Because Reddit's comments have multiple levels, here we consider each level depth to 
                be a separate conversation and contain the entire conversation in a list. Thus there will be 
                duplicate comments if a comment has multiple level follow-ups
    """
    results = google_search(search_query=search_query, api_key=google_api_key, engine_id_cx=reddit_engine_id_cx, num_results=5)
    output_list = clean_search_output(results)
    
    reddit = reddit_setup(client_id=reddit_client_id,client_secret=reddit_client_secret,user=reddit_user)
    search_list = []
    for output in output_list:
        url = output['link']
        post_data = get_post_and_comments(reddit=reddit, url=url)
        search_list.append(post_data)
    return search_list

if __name__=="__main__":
    reddit = reddit_setup(client_id=reddit_client_id,client_secret=reddit_client_secret,user=reddit_user)

    # # Reddit search given link
    # test_urls = [
    #     "https://www.reddit.com/r/japanesestreetwear/comments/q3wshh/where_to_buy_from_japanese_streetwear/",
    #     "https://www.reddit.com/r/streetwear/comments/1g22vzm/clarks_x_tokyo_collection_wallabees/",
    #     "https://www.reddit.com/r/deloitte/comments/1g2psfe/deloitte_global_us_layoffs/",
    # ]
    # url = test_urls[2]
    # submission = reddit.submission(url=url)
    # submission.comments.replace_more(limit=None)
    # comments_list = submission.comments.list()
    # comments_dict = {key:index for index, key in enumerate(comments_list)}

    # comment_conversations = create_comment_conversations(submission)
    # sorted_conversations = sort_comment_conversations(comments_dict, comment_conversations)
    # for conversation in comment_conversations:
    #     for comment in conversation:
    #         print(f"Comment by {comment.author}: {comment.body}")
    #     print("\n\n")
    

    # Search google returned reddit links
    search_query = "nfl week 11 results"
    results = google_search(search_query=search_query, api_key=google_api_key, engine_id_cx=reddit_engine_id_cx, num_results=5)
    output_list = clean_search_output(results)
    search_list = []
    for output in output_list:
        url = output['link']
        post_data = get_post_and_comments(reddit=reddit, url=url)
        search_list.append(post_data)
    search_list