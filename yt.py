
# -*- coding: utf-8 -*-

import os

import google.oauth2.credentials
import requests
from bs4 import BeautifulSoup
import random
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def print_response(response):
  print(response)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
  resource = {}
  for p in properties:
    # Given a key like "snippet.title", split into "snippet" and "title", where
    # "snippet" will be an object and "title" will be a property in that object.
    prop_array = p.split('.')
    ref = resource
    for pa in range(0, len(prop_array)):
      is_array = False
      key = prop_array[pa]

      # For properties that have array values, convert a name like
      # "snippet.tags[]" to snippet.tags, and set a flag to handle
      # the value as an array.
      if key[-2:] == '[]':
        key = key[0:len(key)-2:]
        is_array = True

      if pa == (len(prop_array) - 1):
        # Leave properties without values out of inserted resource.
        if properties[p]:
          if is_array:
            ref[key] = properties[p].split(',')
          else:
            ref[key] = properties[p]
      elif key not in ref:
        # For example, the property is "snippet.title", but the resource does
        # not yet have a "snippet" object. Create the snippet object here.
        # Setting "ref = ref[key]" means that in the next time through the
        # "for pa in range ..." loop, we will be setting a property in the
        # resource's "snippet" object.
        ref[key] = {}
        ref = ref[key]
      else:
        # For example, the property is "snippet.description", and the resource
        # already has a "snippet" object.
        ref = ref[key]
  return resource

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.items():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def comment_threads_insert(client, properties, **kwargs):
  # See full sample for function
  resource = build_resource(properties)

  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.commentThreads().insert(
    body=resource,
    **kwargs
  ).execute()

  return print_response(response)

def scrape(keyword):
    url = 'https://www.youtube.com/results?q={}&sp=CAISAggBUBQ%253D'.format(keyword)
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    f = open(r'data\links.txt', 'w')
    for link in soup.findAll('a', {'class': 'yt-uix-tile-link'}):
        href = link.get('href')
        newhref = href.replace("/watch?v=", "")
        f.write(newhref + '\n')

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()



with open(r'data\comments.txt', 'r') as f:
    foo = [line.strip() for line in f]

# keyword
with open(r'data\keywords.txt', 'r') as f:
    foooo = [line.strip() for line in f]

keywords = open(r'data\keywords.txt', 'r')
x = 10
while x < 20:
    for line in keywords:
        scrape(line)

        with open(r"data\links.txt", 'r+') as f:
            f.readline()
            data = f.read()
            f.seek(0)
            f.write(data)
            f.truncate()

            try:
                with open(r'data\links.txt', 'r') as f:
                    urls = []
                    for url in f:
                        rand = random.choice(foo)

                        comment_threads_insert(client,
                        {'snippet.channelId': 'UCNlM-pgjmd0NNE5I6MzlEGg',
                         'snippet.videoId': url,
                         'snippet.topLevelComment.snippet.textOriginal': rand},
                        part='snippet')
            except:
                pass
            print("Scraping...")
