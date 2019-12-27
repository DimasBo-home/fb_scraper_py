from browser import *
from search import *
from post import *
from methods import *
from fb_user import parser_link_user
import json
import db

browser = None

def open_browser_and_login(func):
	def wrapper(*args):
		global browser
		try:
			browser = get_browser()
		except Exception:
			print("error openBrowser")
			exit(1)
		if browser != None:
			print("OK: [OPEN BROWSER]")
		else:
			print("E: [Open Browser Error] ")
			exit(1)
		if settings.LOGIN_REQUIRED:
			username, password = get_login_credentials()

			if username and password:
				logged_in_browser = login(browser, username, password)

				if logged_in_browser:
					print("OK: [Login Success] <Done>")
				else:
					print ("E: [Login Error] <Problem in logging in (Check your username and password or internet connection)>")
					exit(1)

			else:
				print ("E: [Login Error] <Login Credentials not provided.>")
				exit(1)


		if logged_in_browser and wait_till(browser,"name","q"):
			result = func(*args)
		if browser:
			browser.quit()
		return result
	return wrapper

@open_browser_and_login
def parser_posts(*args):
	global browser
	list_post = args[0]
	global browser
	posts = [] 
	for post_url in list_post:			
		# try:
		data = parser_post(browser,post_url)
		posts.append(data)
		db.request_data(data)
		# except:
			# print ("E: [Read Post Error]")
	return posts

@open_browser_and_login
def parser_user_main(request):
	global browser
	print("[START]")
	print('[User ID] <"{}">'.format(request['id']))
	list_post = []
	try:
		list_post += parser_link_user(browser,request["id"])
		print('Read Success')
	except:
		print("E: [Read search_request Error] ")
		exit(1)
	return list_post

@open_browser_and_login
def parser_search_main(request):
	global browser

	if wait_till(browser,"name","q"):
		print("[START]")
		if "request_date" in request:
			print('[SEARCH] <"{}" "{}">'.format(request['request_text'],request['request_date'].strftime("%Y-%m")))
		else:
			print('[SEARCH] <"{}" >'.format(request['request_text']))
		search_url,search_public_url  = None, None
		try:
			if settings.filter_post_any:
				if "request_date" in request:
					search_url = search_text(browser,request['request_text'],date=(request['request_date'].year,request['request_date'].month))
				else:
					search_url = search_text(browser,request['request_text'])
			if settings.filter_post_public:
				if "request_date" in request:
					search_public_url = search_text(browser,request['request_text'],True,date=(request['request_date'].year,request['request_date'].month))
				else:
					search_public_url =  search_text(browser,request['request_text'],True)
			if search_url:
				search_url = replace_link(search_url,'w')
			if search_public_url:
				search_public_url = replace_link(search_public_url,'w')
		except:
			print("E: [Search Error] ")
			exit(1)
		print("[Read list search_request Success]")
		list_post = []
		try:
			if search_url:
				list_post +=  parser_link_post(browser,request,search_url)
			if settings.filter_public and search_public_url:
				list_post +=parser_link_post(browser,request,search_public_url)
		except:
			print("E: [Read search_request Error] ")
			exit(2)
		print(len(list_post))
		print(list_post)
		print('[Read search_request success]')
		return list_post

if __name__ == '__main__':
	# print("instance:",settings.instance)
	# request = {"request_text":"tesla"}
	# request = get_request()	

	request = {"id":"266419553416728"}

	data_posts = parser_user_main(request)
	save_links("tesla_debug_2",data_posts)
	
	list_data_posts = parting(data_posts,int(len(data_posts)/settings.count_post_iterable))
	print(int(len(data_posts)/settings.count_post_iterable))	
	print(len(list_data_posts))
	
	i = 0
	for list_posts in  list_data_posts:
		i +=1
		print("----------------------------------",i)
		print("----------------------------------",len(list_posts))
		for list_post in list_posts:
			data = parser_posts(data_posts)
			create_json(data,("tesla_debug%s.json" % str(i)))
	# data_post 