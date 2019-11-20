## Description

[![Build Status](https://travis-ci.org/vinitkumar/pycrawler.svg?branch=master)](https://travis-ci.org/vinitkumar/pycrawler)
[![Coverage Status](https://coveralls.io/repos/github/vinitkumar/pycrawler/badge.svg?branch=feature%2Fadd-coverage-coveralls)](https://coveralls.io/github/vinitkumar/pycrawler?branch=feature%2Fadd-coverage-coveralls)

Python Crawler written Python 3. (Supports major Python releases Python3.6, Python3.7 and Python 3.8)

## Installation and Use

### Setup VirtualEnv

```sh
which python3 this will output the path of your python3
#now setup a python3 virtualenv
mkvirtualenv crawl3 -p $(which python3)
```


```sh
workon crawler
python main.py -d5 http://gotchacode.com // -d5 means crawl to the depth of 5.
```

## Results:


And the output is:


```sh
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 50/50 [00:00<00:00, 29200.11it/s]
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 22563.50it/s]
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9/9 [00:00<00:00, 21375.28it/s]
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 22227.37it/s]
CRAWLER STARTED:
https://vinitkumar.me, will crawl upto depth 2
https://vinitkumar.me/
http://changer.nl
https://twitter.com/vinitkme
https://vinitkumar.me/about
https://vinitkumar.github.io/vinit_kumar.pdf
https://vinitkumar.me/values
https://github.com/vinitkumar
https://vinitkumar.me/2013-03-24-life-has-changed/
https://vinitkumar.me/2013-03-24-my-javascript-love/
https://vinitkumar.me/2013-03-27-twitter-like-app-in-nodejs/
http://twitter.com/vinitkme
https://vinitkumar.me/2013-04-07-first-flight-and-vacation-after-months/
====================================================================================================
Crawler Statistics
====================================================================================================
No of links Found: 12
No of followed:     3
Found all links after 0.54s

```

## Issues

Create an issue here if you encounter a bug: [create-issue](https://github.com/vinitkumar/pycrawler/issues/new/choose)




