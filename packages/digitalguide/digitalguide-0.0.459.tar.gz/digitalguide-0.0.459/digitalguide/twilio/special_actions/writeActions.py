import os
from configparser import ConfigParser
from datetime import datetime

import boto3
import requests

from digitalguide.twilio.TwilioUpdate import TwilioUpdate

config = ConfigParser()
config.read("config.ini")

if "space" in config.keys():
    session = boto3.session.Session()
    s3_client = session.client('s3',
                            region_name=config["space"]["region_name"],
                            endpoint_url=config["space"]["endpoint_url"],
                            aws_access_key_id=os.getenv('SPACES_KEY'),
                            aws_secret_access_key=os.getenv('SPACES_SECRET'))

def twilio_write_photo(client, update: TwilioUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName
    update.MediaUrl0

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_" +
                      str(user_id) + '.jpg',
                      Body=requests.get(update.MediaUrl0,
                                        allow_redirects=True).content,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )

def twilio_write_message(client, update: TwilioUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName
    message = update.Body

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_"+str(user_id) + '.txt',
                      Body=message,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )


def twilio_write_voice(client, update: TwilioUpdate, context, bucket, folder):
    user_id = update.WaId
    name = update.ProfileName

    s3_client.put_object(Bucket=bucket,
                      Key=folder + "/" +
                      str(datetime.now())+"_"+str(user_id) + '.mp3',
                      Body=requests.get(update.MediaUrl0,
                                        allow_redirects=True).content,
                      ACL='private',
                      # Metadata={
                      #    'x-amz-meta-my-key': 'your-value'
                      # }
                      )

def twilio_write(client, update: TwilioUpdate, context, bucket, folder):
    if update.MediaContentType0 and update.MediaContentType0.startswith("audio"):
        twilio_write_voice(client, update, context, bucket, folder)
    elif update.MediaContentType0 and update.MediaContentType0.startswith("image"):
        twilio_write_photo(client, update, context, bucket, folder)
    elif update.Body != "":
        twilio_write_message(client, update, context, bucket, folder)
    else:
        raise NotImplementedError("This type of update can not be saved")


twilio_action_functions = {"write_photo": twilio_write_photo,
                             "write_message": twilio_write_message,
                             "write_voice": twilio_write_voice,
                             "write": twilio_write
                             }
