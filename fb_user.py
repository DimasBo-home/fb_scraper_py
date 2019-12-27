from browser import *
import config as settings
import db
from post import idefication_post
import urllib.parse as urlparse
from urllib.parse import parse_qs

def read_posts(browser):
	if is_element(browser,"xpath","//*/a[contains(text(), 'Full Story')]"):
		links = find_elements(browser,"xpath","//*/a[contains(text(), 'Full Story')]")
		posts = []
		for l in links:
			data = idefication_post(l.get_attribute('href'))
			if data['post_id']:
				posts.append(data)
			else:
				print(data)
				print("Error read url:", l.get_attribute('href'))
		return posts
	return None


def parser_link_user(browser,user_id=None,url=None):
	url_open = ""
	posts = []
	if not user_id and not url:
		print("E: [Not parameters]")
		return 1
	elif user_id:
		url_open = settings.https + settings.m_f_link + "/" + user_id
	elif url:
		url_open = url

	open_link(browser,url_open)
	if wait_till(browser,"id","root"):
		links = None
		if is_element(browser,"xpath","//*/a[contains(text(), 'Full Story')]"):
			posts += read_posts(browser)
			db.request_list_user(user_id,posts)
			browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			while (is_element(browser,"xpath","//*[contains(text(), 'Show more')]") or is_element(browser,"xpath","//*[contains(text(), 'See More Stories')]") ) and settings.max_count_post_from_user > len(posts):
				button = None
				if is_element(browser,"xpath","//*[contains(text(), 'See More Stories')]") :
					button = find_element(browser,"xpath","//*[contains(text(), 'See More Stories')]")
				elif is_element(browser,"xpath","//*[contains(text(), 'Show more')]"): 
					button = find_element(browser,"xpath","//*[contains(text(), 'Show more')]").click()

				if button:
					button.click()
					not_wait_till(browser,button)

				browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				if wait_till(browser,"id","root"):
					p = []
					if is_element(browser,"xpath","//*/a[contains(text(), 'Full Story')]"):
						p += read_posts(browser)
					if settings.max_count_post_from_user < (len(posts) + len(p) ):
						cut = len(posts) + len(p) - settings.max_count_post_from_user
						p = p[:cut]
						db.request_list_user(user_id,p)
					if p:
						posts += p

		if settings.max_count_post_from_user < len(posts):
			posts = posts[:settings.max_count_post_from_user]
	else:
		print("E: [open link Error]")
		print("[Parser links post FATAL ]")
		return None
	return posts
