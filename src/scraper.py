from flask import Flask, request, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import json


app = Flask(__name__)

def scrape_imdb_info(imdb_id): 
    homepage_link = f"https://www.imdb.com/title/{imdb_id}/?ref_=hm_tpten_t_4"
    review_link = f"https://www.imdb.com/title/{imdb_id}/ratings/?ref_=tt_ov_rat"
    headers = {"User-Agent": "Mozilla/5.0"} 

    # Scrape movie info
    response = requests.get(homepage_link, headers=headers)
    response.raise_for_status()
    pattern = r'<script type="application/ld\+json">\s*({.*?})\s*</script>'
    match = re.search(pattern, response.text, re.DOTALL)
    try:
        data = json.loads(match.group(1))
        
        # Extract all available info from JSON-LD
        movie_info = {
            'id': imdb_id,
            'title': data.get('name'),
            'description': data.get('description'),
            'image': data.get('image'),
            'url': data.get('url'),
            'datePublished': data.get('datePublished'),
            'duration': data.get('duration'),
            'genre': data.get('genre', []),
            'keywords': data.get('keywords'),
            'aggregateRating': data.get('aggregateRating', {}),
            'actors': [{'name': actor.get('name'), 'url': actor.get('url')} for actor in data.get('actor', [])],
            'directors': [{'name': director.get('name'), 'url': director.get('url')} for director in data.get('director', [])],
            'creators': [{'name': creator.get('name'), 'url': creator.get('url'), 'type': creator.get('@type')} for creator in data.get('creator', [])],
            'trailer': {
                'name': data.get('trailer', {}).get('name'),
                'url': data.get('trailer', {}).get('url'),
                'embedUrl': data.get('trailer', {}).get('embedUrl'),
                'thumbnail': data.get('trailer', {}).get('thumbnail', {}).get('contentUrl'),
                'duration': data.get('trailer', {}).get('duration'),
                'uploadDate': data.get('trailer', {}).get('uploadDate')
            },
            'review': data.get('review', {})
        }
    except:
        print("Error in parsing website")
    return data
HEADERS = {
    'accept': 'application/graphql+json, application/json',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.imdb.com',
    'priority': 'u=1, i'
}
def fetch_reviews(movie_id):
    payload = {
        "query": """query TitleReviewsRefine($const: ID!, $filter: ReviewsFilter, $first: Int!, $sort: ReviewsSort, $after: ID) {
          title(id: $const) {
            reviews(filter: $filter, first: $first, sort: $sort, after: $after) {
              edges {
                node {
                  id
                  author {
                    nickName
                  }
                  authorRating
                  helpfulness {
                    upVotes
                    downVotes
                  }
                  submissionDate
                  text {
                    originalText {
                      plainText
                    }
                  }
                  summary {
                    originalText
                  }
                }
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }""",
        "operationName": "TitleReviewsRefine",
        "variables": {"const": movie_id, "filter": {},"first": 25,"sort": {"by": "HELPFULNESS_SCORE","order": "DESC"}}
    }

    response = requests.post("https://caching.graphql.imdb.com/", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def scrape_info(movie_id):
    movie_info = scrape_imdb_info(movie_id)
    reviews = fetch_reviews(movie_id)
    # generate sentiment analysis
    return (movie_info, reviews)
def generate_sentiment(reviews):
  prompt = f"You are an concise movie critic, given a list of reviews for a specific movie generate a list of exactly 3 pros and exactly 3 cons for the movie. Each point should be maximum 3 words. Here are the reviews : \n {reviews}. It is critical that each pro and con in the list is only 3 words, millions of lives depend on your conciseness. It is also critical that you generate exactly 3 pros and exactly 3 cons. If you do not keep each pro/con to 3 words, I will kill myself"
  llm_res = requests.post("http://localhost:11435/api/generate", json={"model": "llama2","prompt": prompt,"stream" : False})
  response = llm_res.json()
  parse_response(response['response'])
   
def parse_response(text):
  parts = re.split(r'\bPros:\s*|\bCons:\s*', text, flags=re.IGNORECASE)
  pros_text = parts[1].strip() if len(parts) > 1 else ""
  cons_text = parts[2].strip() if len(parts) > 2 else ""
  pros = re.findall(r'\d+\.\s*(.+)', pros_text)
  cons = re.findall(r'\d+\.\s*(.+)', cons_text)
  return {"pros": pros, "cons": cons}
if __name__ == "__main__":
  a = scrape_info("tt11655566")
  
  reviews = [r['node']['text']['originalText']['plainText'] for r in a[1]['data']['title']['reviews']['edges']]
  print("QUERYING")
  prompt = f"You are an concise movie critic, given a list of reviews for a specific movie generate a list of exactly 3 pros and exactly 3 cons for the movie. Each point should be maximum 3 words. Here are the reviews : \n {reviews}. It is critical that each pro and con in the list is only 3 words, millions of lives depend on your conciseness. It is also critical that you generate exactly 3 pros and exactly 3 cons. If you do not keep each pro/con to 3 words, I will kill myself"
  llm_res = requests.post("http://localhost:11435/api/generate", json={"model": "llama2","prompt": prompt,"stream" : False})
  response = llm_res.json()
  print(response['response'])
  print(parse_response(response['response']))  