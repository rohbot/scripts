#from __future__ import print_function
import httplib2
import os
import redis
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors
from apiclient import http
import json
import random
import pyrfc3339

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
PHOTO_TO_DL_HASH = 'photos-to-dl'
DL_PHOTOS_HASH = 'dl-photos'
PHOTO_HASH = 'photos'
PHOTO_DIR = '/home/roh/Pictures/Google/'
r = redis.Redis()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def load_files(service):
  
  req = service.files().list(maxResults=500)
  results = req.execute()
  running = True
  num_photos = 0
  while running:
    items = results.get('items', [])
    if not items:
      print('No files found.')
    else:
      print('Files:')
      for item in items:
        key = item['id']
        #print('{0} ({1})'.format(item['title'], item['id']))
        if item['mimeType'] == 'image/jpeg' and not r.hexists(PHOTO_HASH,key):
          
          photo_data = json.dumps(item)   
          fname = item['originalFilename']
          if fname[-3:].upper() != 'JPG':
            fname = key + ".jpg"
          cdate = pyrfc3339.parse(item['createdDate']).strftime('%s')
          #print item 
          fname = cdate + '_' + fname

          r.hset(PHOTO_TO_DL_HASH,key,fname)
          r.hset(PHOTO_HASH,key,photo_data)
          print fname
          num_photos += 1
        
    req = service.files().list_next(req,results)
    if req: 
      results= req.execute()
    else:
      running = False
    #if num_photos > 3:
    #  running = False  
  print 'Phots Found: ' , num_photos
  #rs = json.dumps(photos)   
  #r.set('photo:json',rs)


def download_files(service):

  keys = r.hkeys(PHOTO_TO_DL_HASH)
  while len(keys) > 0:
    key = random.choice(keys)
    fname = r.hget(PHOTO_TO_DL_HASH,key)
    download_file(service,key,fname)
    keys = r.hkeys(PHOTO_TO_DL_HASH)
  

def download_file(service,key,fname):
  local_fd =  open(PHOTO_DIR+fname, 'w+')
  request = service.files().get_media(fileId=key)
  media_request = http.MediaIoBaseDownload(local_fd, request)
  print 'Downloading: ' + fname
  while True:
    try:
      download_progress, done = media_request.next_chunk()
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      return
    if download_progress:
      print 'Download Progress: %d%%' % int(download_progress.progress() * 100)
    if done:
      print 'Download Complete'
      r.hset(DL_PHOTOS_HASH,key,fname)
      r.hdel(PHOTO_TO_DL_HASH,key)
      return


def get_photo(key):
  return fname


def main():
  """Shows basic usage of the Google Drive API.

  Creates a Google Drive API service object and outputs the names and IDs
  for up to 10 files.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('drive', 'v2', http=http)
  
  load_files(service)
  download_files(service)
  


if __name__ == '__main__':
    main()
