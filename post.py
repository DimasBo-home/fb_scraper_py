import config as settings
import json
from datetime import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
from browser import *
from methods import *
import time
from bs4 import BeautifulSoup

def formater_number(a):
	l = len(a)
	i = 0
	s_int = ''
	maybe_dot = False
	if "." in a:
		maybe_dot = True
	while l > i and s_int == '':
		if maybe_dot:
			while '0' <= a[i] <= '9' or ( a[i] == "." and '0' <= a[i-1] <= '9' ):
				if i+1 < l and (a[i+1] ==  "K" or a[i+1] ==  "M" ):
					s_int += a[i]
					s_int += a[i+1]
					i+=2
				else:			
					s_int += a[i]
					i+=1
				if i == l:
					break
		else:
			while '0' <= a[i] <= '9':
				if i+1 < l and (a[i+1] ==  "K" or a[i+1] ==  "M" ):
					s_int += a[i]
					s_int += a[i+1]
					i+=2
				else:			
					s_int += a[i]
					i+=1
				if i == l:
					break
		i += 1
	if "K" in s_int:
		s_int = float(s_int.replace("K","")) * 10**3
	elif "M" in s_int:
		s_int = float(s_int.replace("M","") )* 10**6
	return int(s_int)

def is_year_in_str(s):
	count = 0
	i = 0
	while count<4 and i<len(s) :
		if s[i].isdigit():
			count += 1
		else:
			count = 0
		i +=1
	if count==4:
		return True
	return False

def formater_date(date):
	if "Yesterday" in date:
		today = datetime.today()
		return today.replace(day=today.day-1).strftime("%Y %B %d")
	elif "hrs" in date:
		return datetime.today().strftime("%Y %B %d")
	elif not is_year_in_str(date):
		return str(settings.YEAR_NOW) +  " " + date
	return date

def parser_comment(browser):
	actor =  find_element(browser,"css","h3 a")
	username = actor.text
	actor_url = formater_url(actor.get_attribute("href"))
	description = find_element(browser,"css","div>div").text
	data = {
		"username":username,
		"actor_url":actor_url,
		"description":description
	}
	
	return data

def parser_likes_post(browser,id,other=False):
	data = {"all" : 0 }
	if other:
		url = "https://mbasic.facebook.com/ufi/reaction/profile/browser/?ft_ent_identifier="+str(id)
		open_link(browser,url)
		if wait_till(browser,"css",".z a"):
			likes = find_elements(browser,"css",".z a")
			l = formater_number(likes[0].text.replace('All',""))
			data["all"] = l

			other_d = []
			for like in likes[1:]:
				smile = find_element(like,"tag","img").get_attribute("src")
				count = formater_number(find_element(like,"tag","span").text)
				other_d.append((smile,count))
			data['other'] = other_d
			return data
	if is_element(browser,"css",'a[href^="/ufi/reaction/profile/browser/"]'):
		like = find_element(browser,"css",'a[href^="/ufi/reaction/profile/browser/"]')
		data["all"] =	formater_number(like.text)
	return data

def parser_count_shares_and_comment(browser,url):
	url = url.replace("mbasic","www")
	open_link(browser,url)
	shares, comment_count = 0,0
	if wait_till(browser,"name","q"):
		el = 0
		while (not wait_till(browser,"css",'a[data-testid="UFI2SharesCount/root"]') or not wait_till(browser,"css",'a[data-testid="UFI2CommentsCount/root"]')) and el < 3:
			el += 1
			print("time")

		if is_element(browser,"css",'a[data-testid="UFI2CommentsCount/root"]'):
			s = BeautifulSoup(find_element(browser,"tag","body").get_attribute("innerHTML"),"lxml")
			comment_count = s.find("a", attrs={'data-testid':"UFI2CommentsCount/root"})
			if comment_count:
				comment_count = formater_number(comment_count.text.replace("Comments",""))
		if is_element(browser,"css",'a[data-testid="UFI2SharesCount/root"]'):
			s = BeautifulSoup(find_element(browser,"tag","body").get_attribute("innerHTML"),"lxml")
			shares = s.find("a", attrs={'data-testid':"UFI2SharesCount/root"})
			if shares:
				shares = formater_number(shares.text.replace("Shares","")) 
	return shares, comment_count
	
def parser_content(browser,type_post):
	date_el = find_element(browser,"tag","abbr")
	date = formater_date(date_el.text)
	date_el = back_el(date_el)
	date_el = back_el(date_el)
	remove_element(browser,date_el)

	if type_post == "photo":
		el_user = find_element(browser,"class","actor-link")
		username = el_user.text
		link_user = el_user.get_attribute("href")
		remove_element(browser,el_user)

		img = find_element(browser,"tag","img").get_attribute("src")

		description = find_element(browser,"class","msg").text
	else:
		content =  find_element(browser,"css","[data-ft]")
		
		el_user = find_elements(content,"css","h3 a")[-1]
		username = el_user.text
		link_user = el_user.get_attribute("href")
		remove_elements(browser, find_elements(content,"css","h3 a"))
		
		description = content.text

		img = None
		is_img = find_element(content,"css","a img")
		if is_img:
			img = find_back_a(is_img).get_attribute("href")
	data = {
		"username": username,
		"link_user":link_user,
		"img":img,
		"description":description,
		"date":date,
	}
	return data

def parser_post(browser,data,like_other= False):
	if not data["post_id"]:
		data = idefication_post(data['url'])
	if like_other:
		data["likes"] = parser_likes_post(browser,data["post_id"],other = like_other)
	
	open_link(browser,data['url'])
	if wait_till(browser,"id","root"):
		root = find_element(browser,"id","root")
		data["content"] = parser_content(browser,data["type"])
		if not like_other:
			data["likes"] = parser_likes_post(browser,data["post_id"])["all"]

	data['comments'] = parser_comments(browser)

	count = parser_count_shares_and_comment(browser,data['url'])

	data["shares"] = count[0]
	data["comment_count"] = count[1]

	return data

def idefication_post(url):
	parsed = urlparse.urlparse(url)
	parsed_q = parse_qs(parsed.query)
	parsed_path = parsed.path[1:].split('/')
	post_id, actor_id, type_post = None, None, None
	if "/story.php" in url:
		post_id =  parsed_q["story_fbid"][0]
		actor_id = parsed_q["id"][0]
		type_post = "story"
	elif "/groups/" in url:
		post_id = parsed_q["id"][0]
		actor_id = parsed_path[1]
		type_post = "group"
	elif "/photos/" in url:
		post_id = parsed_path[3]
		actor_id = parsed_path[0]
		type_post = "photo"
	elif 'photo.php' in url:
		type_post = "photo"
		post_id = parsed_q["fbid"][0]
		actor_id = parsed_q["id"][0]
	elif '/events/' in url:
		type_post = "event"
		post_id = parsed_path[1]
	else:
		for key in parsed_q.keys():
			if key =="story_fbid":
				post_id =  parsed_q["story_fbid"][0]
				break
			elif key =="id":
				post_id = parsed_q["id"][0]
				break
			elif key =="fbid":
				post_id = parsed_q["fbid"][0]
				break
	data = {
		"type": type_post,
		"url" : url,
		"post_id" : post_id,
		"actor_id" : actor_id,
	}
	return data

def parser_comment(browser,header):
	username = header.text
	actor_url = header.get_attribute("href")
	
	comment = back_el(header)
	comment = back_el(comment)
	remove_element(browser,header)

	panel = back_el(find_element(comment,"tag",'abbr'))
	remove_element(browser,panel)
	replies_link = None
	replies = find_element(comment,"css",'a[href^="/comment/replies/"]')
	if replies:
		replies_link = replies.get_attribute("href")
		remove_element(browser,replies)

	description = comment.text
	
	comment = {
		"username": username,
		"actor_url": actor_url,
		'description':description,
		"replies_link":replies_link,
	}
	return comment

def parser_comments(browser):
	count = settings.max_count_comment
	i = 0
	now_page = False
	headers = find_elements(browser,"xpath","//*/h3/a")
	if len(headers) > count:
		headers = headers[count:]
		now_page =True

	if len(headers) <= count:
		now_page =True
	data = []

	for h in headers:
		data.append(parser_comment(browser,h))
		i += 1
	if now_page:
		return data

	while wait_till(browser ,"xpath",'.//*[text()=""View more comments…"]') and count > i:
		find_back_a(find_element(browser ,"xpath",'.//*[text()=""View more comments…"]')).click()	
		if wait_till(browser,"id","root"):
			headers = find_elements(browser,"xpath","//*/h3/a")
			for h in headers:
				data.append(parser_comment(browser,h))
				i += 1
	return data