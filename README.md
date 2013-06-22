mp3panda-downloader
===================

code by ziozzang@gmail.com

MP3Panda Generic Downloader. You can download automatically from MP3Panda the tracks what you bought.

Prerequiste
===========

```
apt-get install python-bs4 python-mutagen

or

pip install beautifulsoup4
pip install mutagen
```

mutagen and beautifulsoup4 is required for execute. tested Python 2.7 on debian.

Configuration
=============

edit your ID and Password on file. after then execute script.
the script will be run infinite wait for next queue like daemon.

Execution
=========

```
./download.py > log 2> error &
```

this will run like daemon. you just buy album or song at web site.
