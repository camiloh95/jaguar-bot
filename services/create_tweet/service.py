import os
import S3
import tweepy
import requests
import dynamodb

def create_tweet(event, context):
  imagesFolderPath = os.environ['IMAGES_FOLDER_PATH']
  itemToPublish = None

  try:
    tableName='tweets'
    items = dynamodb.get_items(tableName='tweets')
    for item in items['Items']:
      if item['published']['BOOL'] == False:
        itemToPublish = item
        text = item['text']['S']
        imagesFolder = item['images_folder']['S']
        break

    if itemToPublish == None:
      return {
        'message': 'there are no more tweets to publish'
      }

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

    imagesResponse = S3.download_bot_images(imagesFolder)

    if imagesResponse == 'empty folder':
      images = os.listdir(imagesFolderPath)
      mediaIds = []
      for image in images:
        response = api.media_upload(filename=f'{imagesFolderPath}/{image}')
        mediaId = getattr(response, 'media_id_string')
        mediaIds.append(mediaId)
      response = client.create_tweet(text=text, media_ids=mediaIds)
    else:
      response = client.create_tweet(text=text)
    dynamodb.update_publish(tableName, itemToPublish)
  except requests.RequestException as e:
    raise e 

  return response