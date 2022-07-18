import os
import S3
import tweepy
import requests
import dynamodb

def create_tweet(event, context):
  try:
    items = dynamodb.get_items()
    text = items['Items'][0]['message']['S']
    images_folder = items['Items'][0]['images_folder']['S']

    S3.download_bot_images(images_folder)

    auth = tweepy.OAuthHandler(
      os.environ['TWITTER_CONSUMER_KEY'],
      os.environ['TWITTER_CONSUMER_SECRET']
    )
    auth.set_access_token(
      os.environ['TWITTER_ACCESS_TOKEN'],
      os.environ['TWITTER_TOKEN_SECRET']
    )
    api = tweepy.API(auth)
    client = tweepy.Client(
      bearer_token=os.environ['TWITTER_BEARER_TOKEN'],
      consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
      consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
      access_token=os.environ['TWITTER_ACCESS_TOKEN'],
      access_token_secret=os.environ['TWITTER_TOKEN_SECRET']
    )

    images = os.listdir('/tmp/bot_images')
    media_ids = []
    for image in images:
      response = api.media_upload(filename=f'/tmp/bot_images/{image}')
      media_id = getattr(response, 'media_id_string')
      media_ids.append(media_id)

    response = client.create_tweet(text=text, media_ids=media_ids)
  except requests.RequestException as e:
    print(e)
    raise e 

  return response