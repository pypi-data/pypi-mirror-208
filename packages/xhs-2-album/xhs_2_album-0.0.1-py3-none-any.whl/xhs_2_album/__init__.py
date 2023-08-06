#!/usr/bin/env python3

# -*- coding: utf-8 -*-

name = 'xhs_2_album'

from telegram_util import AlbumResult as Result
from bs4 import BeautifulSoup
import re
import cached_url
import yaml
import time
with open('credential') as f:
    credential = yaml.load(f, Loader=yaml.FullLoader)

def formatUrl(url):
    if url.startswith("http://xhslink"):
        json = cached_url.get('http://api.dwzjh.com/api/reduction?url=' + url, force_cache=True)
        json = yaml.load(json, Loader=yaml.FullLoader)
        url = json.get('longurl')
        url = url.split('?')[0]
    return url.replace("/explore/", "/discovery/item/")

headers = {"user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X)",}
def getJson(url):
    try:
        return getJsonImp(url, ttl=float('Inf'))
    except:
        time.sleep(0.01)
        return getJsonImp(url, ttl=0.001)

def getJsonImp(url, ttl=float('Inf')):
    url = formatUrl(url)
    content = cached_url.get(url, ttl=ttl, headers=headers)
    soup = BeautifulSoup(content, 'html.parser')
    json = soup.find("script", string=re.compile("__INITIAL_STATE__")).text[25:]
    json = yaml.load(json, Loader=yaml.FullLoader)
    data = json['noteData']['data']['noteData']
    return data 

# def addSchema(traceId):
#     return 'https://sns-img-hw.xhscdn.com/' + traceId

def addSchema(url):
    if not url:
        return ''
    if url.startswith('http'):
        return url
    return 'https:' + url

def get(url):
    url = formatUrl(url)
    json = getJson(url)
    r = Result()
    r.imgs = [addSchema(item['url']) for item in json['imageList']]
    r.video = addSchema(json.get('video', {}).get('url'))
    r.cap_html_v2 = json['desc']
    if json['title']:
        r.cap_html_v2 = '【%s】\n\n%s' % (json['title'], json['desc'])
    r.url = url
    return r