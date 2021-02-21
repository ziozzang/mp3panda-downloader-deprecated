# Deprecated Project. Archived.
# Use this-->>> https://github.com/ziozzang/mp3panda-downloader
* WARNING: mp3panda doesn't support rpc server and any downloaders any more.

mp3panda-downloader
===================

code by ziozzang@gmail.com

MP3Panda Generic Downloader. You can download automatically from MP3Panda the tracks what you bought.

the MP3Panda is cheap mp3 download site. URL is http://www.mp3panda.com

Prerequiste
===========

```
apt-get install python-bs4 python-mutagen

or

pip install beautifulsoup4
pip install mutagen
```

mutagen and beautifulsoup4 is required for execute. tested Python 2.7 on debian.

```
apt-get install axel
```


this script use 'axel' as downloader. so, you must install axel.

Configuration
=============

edit your ID and Password on file. after then execute script.
the script will be run infinite wait for next queue like daemon.

This downloader maybe support another mp3 site such like MP3Cake, MP3Eagle or MP3Fiesta.
Check source file. change RPC address on source file.

```
# For MP3Cake: http://rpc.mp3cake.com
# For MP3Eagle: http://rpc.mp3eagle.com
# For MP3Fiesta: http://rpc.mp3fiesta.com
```

Execution
=========

```
./download.py > log 2> error &
```

this will run like daemon. you just buy album or song at web site.

Function
========

* download files.
* Rename with directory formated.
* update basic information and album art into ID3 Tag in MP3.
* Keep Downloaded files history with DB.
