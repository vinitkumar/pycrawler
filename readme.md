## Description

A simple crawler written in Python (3.5+).

## Installation and Use

### Setup VirtualEnv

```sh
which python3.5 # this will output the path of your python3.5 
#now setup a python3 virtualenv
mkvirtualenv crawl3 -p /Library/Frameworks/Python.framework/Versions/3.5/bin/python3.5
```


```sh
$ pip3 install pycrawler
$ python crawler.py -d5 http://gotchacode.com // -d5 means crawl to the depth of 5.
```

## Results:

The Library is now ported to Python3, The results also showcase the different in speed.


Results for latest python3 compatible library:

```sh
CRAWLER STARTED:
http://gotchacode.com, will crawl upto depth 5
===============================================================
http://gotchacode.com/
http://gotchacode.com/about
http://github.com/vinitkumar
http://vinitkumar.me
http://www.changer.nl
https://gratipay.com/vinitkme/
http://gotchacode.com/2014/06/12/On-Using-What-You-Already-Have.html
http://gotchacode.com/2014/05/01/the-pragmatic-programmer-checklist.html
http://gotchacode.com/2014/02/26/simple-state-machine-framework-in-c-number.html
http://gotchacode.com/2014/02/15/setup-a-local-gitignore-without-messing-up-project.html
http://gotchacode.com/2014/02/14/how-to-use-facebook-page-albums-as-image-source-in-django.html
http://gotchacode.com/2014/02/13/migrating-to-octopress.html
http://gotchacode.com/2014/01/music-movies-and-life.html
http://gotchacode.com/2014/01/happy-new-year-2014.html
http://gotchacode.com/page2
https://twitter.com/vinitkme
https://twitter.com/share
http://disqus.com/?ref_noscript
http://disqus.com


Crawler Statistics
==================
No of links Found: 19
No of follwed:     3
Time Stats : Found all links  after 2.52s
```

## Issues

Create an issue in case you found a bug




