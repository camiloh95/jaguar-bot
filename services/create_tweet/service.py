import os
import requests
from dynamodb import get_items
from requests_oauthlib import OAuth1

def create_tweet(event, context):
  try:
    items = get_items()
    message = items['Items'][0]['message']['S']
    body = {'text': message}
    url = os.environ['TWITTER_API_URL']
    auth = OAuth1(os.environ['TWITTER_CONSUMER_KEY'],
                  os.environ['TWITTER_CONSUMER_SECRET'],
                  os.environ['TWITTER_ACCESS_TOKEN'],
                  os.environ['TWITTER_TOKEN_SECRET'])
    request = requests.post(url, json=body, auth=auth).json()
    request
  except requests.RequestException as e:
    print(e)
    raise e

  return request