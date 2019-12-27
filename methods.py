# from browser import *
import config as settings
import json
from math import ceil

def parting(xs, parts):
	part_len = ceil(len(xs)/parts)
	return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]

def create_json(data,filename):
	with open(filename, "w") as write_file:
		json.dump(data, write_file, indent=4)

def append_json(data,filename):
	with open(filename, "a") as write_file:
		json.dump(data, write_file)

def save_links(name,posts):
	with open(("data/%s.txt" % name) ,"w") as f:
		for item in posts:
			f.write(item['url'] + "\n")

def print_message(string):
	print("---------------",string,"---------------")

def cut_link(url):
	try:
		if len(url) > 1600:
			return url[:1600]
	except TypeError:
		pass
	return url

def replace_link(url,p='m'):
	try:
		if url == None:
			return url
		if p == 'm':
			return url.replace('mbasic','www')
		elif p == 'w':
			return url.replace('www','mbasic')
	except TypeError:
		pass
	return url