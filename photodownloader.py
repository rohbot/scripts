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

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
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


def get_files(service):
  
  req = service.files().list(maxResults=500)
  results = req.execute()
  running = True
  photos = []
  while running:
    items = results.get('items', [])
    if not items:
      print('No files found.')
    else:
      print('Files:')
      for item in items:
        #print('{0} ({1})'.format(item['title'], item['id']))
        if item['mimeType'] == 'image/jpeg':
          photos.append(item)         
          fname = item['title']
          print fname
        #fd = open(fname,'w')
          #download_file(service, item['id'],fd)
          #print items[1]
    req = service.files().list_next(req,results)
    if req: 
      results= req.execute()
    else:
      running = False
  print len(photos)
  rs = json.dumps(photos)   
  r.set('photo:json',rs)


def download_file(service, file_id, local_fd):
  """Download a Drive file's content to the local filesystem.

  Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
  """
  request = service.files().get_media(fileId=file_id)
  media_request = http.MediaIoBaseDownload(local_fd, request)

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
      return

def download_files(service):

  rs = r.get('photo:json')
  results = json.loads(rs)
  

def generare_index():
  rs = r.get('photo:json')
  results = json.loads(rs)
  print len(results)

  html = """
  <html>
  <header>
  <title> My Photos </title>
  </header>
  """
  img = """<a href= '%s'><img src = '%s'></img></a>
  """

  count = 1
  for item in results:
  #item = results[0]
    if item['mimeType'] == 'image/jpeg':
      title = item['title']
      id = item['id']
      dl = item['webContentLink']
      thumb = item['thumbnailLink']   
      #print item['title'] , item['id'], link
      #redis.hset('photos', item['id'], json.dumps(item))
      html += img % (dl,thumb)
      if count % 6 == 0:
        html += "<br/>"
  #b = json.loads(redis.get('photo:id:' + item['id']))
  #print b['title']

  f = open('index.html', 'w')
  f.write(html)
  f.close()

def main():
  """Shows basic usage of the Google Drive API.

  Creates a Google Drive API service object and outputs the names and IDs
  for up to 10 files.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('drive', 'v2', http=http)
  
  download_files(service)
  


if __name__ == '__main__':
    main()
