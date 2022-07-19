import os
import S3
import tweepy
import requests
import dynamodb

def create_tweet(event, context):
  images_folder_path = os.environ['IMAGES_FOLDER_PATH']

  try:
    tableName='tweets'
    items = dynamodb.get_items(tableName='tweets')
    for item in items['Items']:
      if item['published']['BOOL'] == False:
        item_to_publish = item
        text = item['text']['S']
        images_folder = item['images_folder']['S']
        break

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

    images = os.listdir(images_folder_path)
    media_ids = []
    for image in images:
      response = api.media_upload(filename=f'{images_folder_path}/{image}')
      media_id = getattr(response, 'media_id_string')
      media_ids.append(media_id)

    response = client.create_tweet(text=text, media_ids=media_ids)
    dynamodb.update_publish(tableName, item_to_publish)
  except requests.RequestException as e:
    raise e 

  return response