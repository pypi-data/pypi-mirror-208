#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'twitter_2_album'

import yaml
from telegram_util import AlbumResult as Result
from telegram_util import compactText, matchKey
import tweepy
import json
import html
import pkg_resources

with open('CREDENTIALS') as f:
	CREDENTIALS = yaml.load(f, Loader=yaml.FullLoader)
auth = tweepy.OAuthHandler(CREDENTIALS['twitter_consumer_key'], CREDENTIALS['twitter_consumer_secret'])
auth.set_access_token(CREDENTIALS['twitter_access_token'], CREDENTIALS['twitter_access_secret'])
twitterApi = tweepy.API(auth)

def getTid(path):
	index = path.find('?')
	if index > -1:
		path = path[:index]
	return path.split('/')[-1]

def getCap(status):
	# full_text for long tweet is not retrievable by api yet
	# https://github.com/tweepy/tweepy/discussions/2074
	text = list(status.full_text)
	for x in status.entities.get('media', []):
		for pos in range(x['indices'][0], x['indices'][1]):
			text[pos] = ''
	text = html.unescape(''.join(text))
	for x in status.entities.get('urls', []):
		if x['expanded_url'] == 'https://twitter.com/i/web/status/' + str(status.id):
			text = text.replace(x['url'], '')
		elif len(x['expanded_url']) < 30:
			text = text.replace(x['url'], ' ' + x['expanded_url'])
			text = text.replace('  ' + x['expanded_url'], ' ' + x['expanded_url'])
		else:
			text = text.replace(x['url'], '[%s](%s)' % ('link', x['expanded_url']))
	text = compactText(html.unescape(text))
	return text

def getEntities(status):
	try:
		return status.extended_entities
	except:
		return status.entities

def getMediaUrl(item):
	if item['type'] == 'photo':
		return item['media_url'] + '?name=large'
	variants = [x for x in item['video_info']['variants'] if x['content_type'] == 'video/mp4']
	variants = [(x.get('bitrate'), x) for x in variants]
	variants.sort()
	return variants[-1][1]['url']

def getImgs(status):
	if not status:
		return []
	return [getMediaUrl(x) for x in getEntities(status).get('media', []) if getMediaUrl(x)]

def isPlainRetweet(status):
	try:
		if not status.retweeted_status:
			return False
	except:
		return False
	if status.in_reply_to_status_id:
		return False
	return True

def getQuote(status, func):
	result = func(status)
	try:
		result = result or func(status.quoted_status)
	except:
		...

	try:
		result = result or func(status.retweeted_status)
	except:
		...

	try:
		result = result or func(status.retweeted_status.quoted_status)
	except:
		...

	return result

def getInReplyToLink(status):
	if status.in_reply_to_screen_name and status.in_reply_to_status_id:
		return ' [origin](https://twitter.com/%s/status/%d)' % (status.in_reply_to_screen_name, status.in_reply_to_status_id)
	return ''

def _get(status):
	r = Result()
	r.imgs = getQuote(status, getImgs) or []
	r.cap = getCap(status) + getInReplyToLink(status)
	if r.cap.startswith('RT '):
		try:
			r.cap = getCap(status.retweeted_status)
		except:
			...
	return r

def getUnroll(status):
	status_list = [status]
	heuristic = 1.001
	while True:
		statuses = twitterApi.user_timeline(user_id = status.user.id, since_id = status.id, max_id = int(status.id * heuristic), count = 200)[::-1]
		if len(statuses) != 200:
			break
		heuristic = (heuristic - 1) / 2 + 1
	for status in statuses:
		if status.in_reply_to_status_id == status_list[-1].id:
			status_list.append(twitterApi.get_status(status.id, tweet_mode="extended"))
	result = Result()
	for status in status_list:
		result.imgs += getImgs(status)
		result.cap = result.cap + '\n\n' + getCap(status)
	return result
	

def getCanonicalStatus(tid):
	status = twitterApi.get_status(tid, tweet_mode="extended")
	if isPlainRetweet(status):
		return status.retweeted_status
	return status

def nomalizeResultUrl(r, path, status):
	if matchKey(path, ['twitter', 'http']):
		r.url = path
	else:
		r.url = 'http://twitter.com/%s/status/%s' % (
			status.user.screen_name or status.user.id, status.id)
	return r

def get(path, unroll=False):
	path = str(path)
	tid = getTid(path)
	status = getCanonicalStatus(tid)
	if unroll:
		r = getUnroll(status)
	else:
		r = _get(status)
	return nomalizeResultUrl(r, path, status)