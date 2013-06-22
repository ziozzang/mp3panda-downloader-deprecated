#!/usr/bin/python
#########################################################################
# MP3Panda Generic Downloader for Linux
# - Code by Jioh L. Jung (ziozzang@gmail.com)

import urllib2
import md5
import string
import os
import shutil
import anydbm
import time
from bs4 import BeautifulSoup
from mutagen import id3


###############################
# configure
user_id = "FIXME!!!(E-MAIL ADDRESS!!)"
user_pw = "FIXME!!!(password!!)"

# The Prefix of download path.
TARGET_PATH = u"/home/ziozzang/nas/Music"
# The Directory Structure of.
# Same as fiesta downloader.
DEFAULT_FORMAT = u"{artist}/{album}_({year})/{track}_{song}.mp3"
# Temporary File Name.
tempfile = u"a.mp3"
# concurrent download session for 1 file. just like flashget or something..
CONNECTION_FOR_FILE = 5
# default Agent for downloading.
DEFAULT_AGENT="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"
# Basic RPC url. you can change this if you use another site.
# For MP3Cake: http://rpc.mp3cake.com
# For MP3Eagle: http://rpc.mp3eagle.com
# For MP3Fiesta: http://rpc.mp3fiesta.com
base_url = "http://rpc.mp3panda.com/"
# Download history save db file
DBFILE = "savedlist.db"
# Check Interval for new queues.
SLEEP_INTERVAL = 3
# if LOOP_SEESION is counted(the number sleep counted)
#  refresh new session_id
LOOP_SESSION = 1000

###############################
def get_session(login_id, login_pw):
  global base_url
  URL = "{base}fman.php?action=login&login={id}&password={pw}".format(
    id=string.replace(login_id, "@", "%40"), 
    pw = md5.new(login_pw.strip()).hexdigest(),
    base = base_url
  )
  response = urllib2.urlopen(URL)
  content = response.read()
  soup = BeautifulSoup(content)
  sid = soup.fmanager.session_id.string
  return sid

def get_list(sid):
  global base_url
  d = []
  URL = "{base}/fman.php?session_id={sid}&action=get_new_ids".format(
    sid = sid,
    base = base_url
  )
  response = urllib2.urlopen(URL)
  content = response.read()
  soup = BeautifulSoup(content)
  for i in  soup.fmanager.tracks.find_all("id"):
    d.append(str(i.string))
  return d

def get_info(sid, trkid):
  global base_url
  d = []
  URL = "{base}/fman.php?session_id={sid}&action=get_track_info&track_id={tid}".format(
    sid = sid, tid = trkid,
    base = base_url
  )
  response = urllib2.urlopen(URL)
  content = response.read()
  soup = BeautifulSoup(content)
  d = soup.fmanager
  i = {}
  i['url'] = d.url.text
  i['title'] = d.title.text
  i['track_num'] = d.track_num.text
  i['performer_id'] = d.performer_id.text
  i['performer'] = d.performer.text
  i['album_id'] = d.album_id.text
  i['album_title'] = d.album_title.text
  i['album_year'] = d.album_year.text
  i['expiration_time'] = d.expiration_time.text
  i['file_size'] = d.file_size.text
  i['checksum'] = d.checksum.text
  i['error_status'] = d.error_status.text
  print " >> INFO // =================================="
  print " >> ARTIST: '%s' ALBUM: '%s' YEAR:%s" % (i['performer'], i['album_title'], i['album_year']) 
  print " >> TRACK: %s TITLE: '%s'" % (i['track_num'],i['title'])
  print " >> STATUS: %s / FILESIZE: %s" % (i['error_status'],i['file_size'])
  return i

def get_cover(i):
  print " >> Fetch Album Cover... ",
  performer_id = str(i['performer_id'])
  album_id = str(i['album_id'])
  URL = "http://covers.mp3panda.com/{psid}/{pid}/alb_{aid}_big2.jpg".format(
    psid=performer_id[:2], pid=performer_id, aid=album_id)
  response = urllib2.urlopen(URL)
  content = response.read()
  print "done"
  i['album_art']=content
  return content

def update_tags(i, fn="a.mp3"):
  commnet = u"source=MP3PANDA\nURL:{url}\nArtistID={pid}\nAlbumID={aid}".format(
    url=i['url'], aid=i['album_id'], pid=i['performer_id']
  )
  audio = id3.ID3(fn)
  audio.add(id3.TRCK(encoding=3, text=i['track_num']))
  audio.add(id3.TIT2(encoding=3, text=i['title']))
  audio.add(id3.TPE1(encoding=3, text=i['performer']))
  audio.add(id3.TALB(encoding=3, text=i['album_title']))
  audio.add(id3.TDRC(encoding=3, text=i['album_year']))
  #audio.add(id3.TCON(encoding=3, text=u"Genre"))
  audio.add(id3.COMM(encoding=3, text=u"Comment"))
  p = get_cover(i)
  audio.add(id3.APIC(encoding=3, mime='image/jpeg', type=3, desc='Front Cover', data=p))
  audio.save()

def safe_replace(s):
  s = string.replace(s, u"/", u"_")
  s = string.replace(s, u"\\", u"_")
  s = string.replace(s, u"?", u"_")
  s = string.replace(s, u"<", u"_")
  s = string.replace(s, u">", u"_")
  s = string.replace(s, u"%", u"_")
  return s

def get_file(i, fn="a.mp3"):
  global CONNECTION_FOR_FILE, DEFAULT_AGENT
  cmd = "axel -q --num-connections={con} --output={fname} --user-agent=\"{agent}\" {url}".format(
    con=CONNECTION_FOR_FILE, agent=DEFAULT_AGENT, fname=fn, url=str(i['url'])
  )
  res = os.system(cmd)
  if res != 0:
    return False
  return True

def get_fname(i):
  global DEFAULT_FORMAT
  fname = DEFAULT_FORMAT.format(
    artist= safe_replace(i['performer']),
    album= safe_replace(i['album_title']),
    year = i['album_year'],
    track = i['track_num'],
    song = safe_replace(i['title']),
  )
  print " >> Filename will be: %s" % fname
  return fname

def check_fileexist(fname):
  global TARGET_PATH
  return os.path.exists(u"%s/%s" % (TARGET_PATH, fname))

def move_to(fn, fname):
  global TARGET_PATH
  tname = u"%s/%s" % (TARGET_PATH, fname)
  dir = os.path.dirname(tname)
  if not os.path.exists(dir):
    os.makedirs(dir)
  return shutil.move(fn, tname)


def LOOPER(session_id):
  #LOOP START HERE..
  global DBFILE, tempfile
  fids = get_list(session_id)
  #print "Total Count is %d" % len(fids)

  db = anydbm.open(DBFILE,"c")
  for i in fids:
    if db.has_key(i):
      continue
    print " >==================================="
    print " > Progress %s" % i
    j = get_info(session_id, i)
    if len(j['url']) == 0:
      print " >> Error No URL found!"
      db[i] = "0"
      continue
    nm = get_fname(j)
    if check_fileexist(nm):
      print " >> Already Exist: SKIP!"
      db[i] = "0"
      continue
    if os.path.exists(tempfile):
      os.remove(tempfile)
    if not get_file(j, tempfile):
      print " >> Fatch Failed!"
      db[i] = "0"
      continue
    update_tags(j, tempfile)
    print " >> File ID3 Tag Updated"
    move_to(tempfile, nm)
    print " >> File Process OK!"
    db[i] = "1"
  db.close()

while True:
  session_id = get_session(user_id, user_pw)
  for i in range(LOOP_SESSION):
    LOOPER(session_id)
    time.sleep(SLEEP_INTERVAL)

