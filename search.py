from browser import *
import config as settings
from post import idefication_post
import db
import urllib.parse as urlparse
from urllib.parse import parse_qs

def click_filter(el):
	while el.tag_name != 'a':
		el = el.find_element_by_xpath('..')
	el.click()

def filter_publick(browser):
	try:
		wait_till(browser,"css",'[@data-testid="filters_container"]')
		el = find_element(browser,"xpath","//*[text()='Public']/..")
		click_filter(el)
		return True
	except Exception as e:
		print("[Public Fatal]")
		return False

def parser_link_post(browser,request,url):
	open_link(browser,url)
	links = find_elements(browser,"xpath","//*/a[contains(text(), 'Full Story')]")
	posts = []
	for l in links:
		data = idefication_post(l.get_attribute('href'))
		if data['post_id']:
			posts.append(data)
		else:
			print(data)
			print("Error read url:", l.get_attribute('href'))
			if posts:
				return None
			else:
				return posts
	
	db.request_list_search(request,posts)
	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	while wait_till(browser,"css",'#see_more_pager a') and len(posts) < settings.max_count_post_from_search:
		button = find_element(browser,"css",'#see_more_pager a')

		if button:
			button.click()
			not_wait_till(browser,button)
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
		if wait_till(browser,"id","root"):
			list_url = []
			for l in find_elements(browser,"xpath","//*/a[contains(text(), 'Full Story')]"):
				data = idefication_post(l.get_attribute('href'))
				if data['post_id']:
					list_url.append(data)
				else:
					print(data)
					print("Error read url:", l.get_attribute('href'))

			if settings.max_count_post_from_search < (len(posts) + len(list_url)):
				cut = len(posts) + len(list_url) - settings.max_count_post_from_user
				list_url = list_url[:cut]
			db.request_list_search(request,list_url)
			posts += list_url
		not_wait_till(browser,wait_till(browser,"id","root"))
		
	if len(posts) > settings.max_count_post_from_search:
		posts = posts[:settings.max_count_post_from_search]
	return posts

def set_valuer_select(browser,value):
	wait_till(browser,"css",'[data-testid="filters_container"]')
	filter_panel = find_element(browser,"css",'[data-testid="filters_container"]')
	date_panel = find_element(filter_panel,"xpath",'.//*[text()="DATE POSTED"]/..')
	
	find_element(date_panel,"xpath",".//*[text()='Choose a Date...']").click()
	
	el = find_element(date_panel,"css",'input:checked')
	el = back_el(back_el(el))
	
	links = find_elements(el,"css",'a')[-1].click()
	selects = find_elements(browser,"css","ul[role='menu'] li.__MenuItem")
	if (int(years[-1].text) <= date[0] <= settings.YEAR_NOW):
		print("test")
		index = settings.YEAR_NOW - date[0]
		years[index].click()
			
def filter_date(browser,date):
	wait_till(browser,"css",'[data-testid="filters_container"]')
	filter_panel = find_element(browser,"css",'[data-testid="filters_container"]')
	date_panel = find_element(filter_panel,"xpath",'.//*[text()="DATE POSTED"]/..')
	if len(date) == 1 and (settings.YEAR_NOW >= date[0] >= settings.YEAR_NOW - 4):
		links = find_elements(date_panel, "css","a")
		if "any date" == date[0]:
			links[0].click()
		elif date[0] == settings.YEAR_NOW:
			links[1].click()
		elif date[0] == (settings.YEAR_NOW-1):
			links[2].click()
		elif date[0] == (settings.YEAR_NOW-2):
			links[3].click()
	else:
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		find_element(date_panel,"xpath",".//*[text()='Choose a Date...']").click()
		el = find_element(date_panel,"css",'input:checked')
		el = back_el(back_el(el))			
		links = find_elements(el,"css",'a')[-1].click()
		items = find_elements(browser,"css","ul[role='menu'] li.__MenuItem")
		# 2019 18 17 16 15 -04
		#  0	1	2 3 4
		if (int(items[-1].text) <= date[0] <= settings.YEAR_NOW):
			index = settings.YEAR_NOW - date[0]
			items[index].click()
			not_wait_till(browser,items[index])

		if len(date) == 2 and wait_till(browser,"name",'q'):
			wait_till(browser,"css",'[data-testid="filters_container"]')
			filter_panel = find_element(browser,"css",'[data-testid="filters_container"]')
			browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			date_panel = find_element(filter_panel,"xpath",'.//*[text()="DATE POSTED"]/..')
			find_element(date_panel,"xpath",".//*[text()='Choose a Date...']").click()
			el = find_element(date_panel,"css",'input:checked')
			el = back_el(back_el(el))			
			links = find_elements(el,"css",'a')[-2].click()
			items = find_elements(browser,"css","ul[role='menu'] li.__MenuItem")[16:]
			index = date[1]
			items[index].click()
			not_wait_till(browser,items[index])
		else:
			print('E: [month Error] <puting not month>')


def search_text(browser,word,publick=False,date=None,filters=None):
	fb_path = "https://www.facebook.com/search/posts/?q=" + word
	open_link(browser,fb_path)

	wait_till(browser,"xpath","//*[contains(text(), 'Public')]")
	# is publick post
	if publick:
		filter_publick(browser)
	wait_till(browser,"xpath",'//*[@data-testid="filters_header"]')
	# is date
	if date:
		filter_date(browser,date)
	wait_till(browser,"css",'[data-testid="filters_container"]')
	if wait_till(browser,"xpath",'//*[contains(text(), "We couldn\'t find anything for")]'):
		return None
	# i =  0
	# while not wait_till(browser,"xpath","//*/a[contains(text(), 'See All')]") and i < 3:
	# 	browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	# 	i += 1
	# if wait_till(browser,"xpath","//*/a[contains(text(), 'See All')]"):
	# 	element = find_elements(browser,"xpath","//*/a[contains(text(), 'See All')]")[-1]
	# 	element.click()
	# 	not_wait_till(browser,element)
	# wait_till(browser,"css",'[data-testid="filters_container"]')
	return browser.current_url

def test():
	browser = get_browser()
	if settings.LOGIN_REQUIRED:
		username, password = get_login_credentials()

		if username and password:
			logged_in_browser = login(browser, username, password)

			if logged_in_browser:
				print("OK: [Login Success] <Done>")
				# return logged_in_browser
			else:
				print ("E: [Login Error] <Problem in logging in (Check your username and password or internet connection)>")
				exit(1)

		else:
			print ("E: [Login Error] <Login Credentials not provided.>")
			exit(1)
	if wait_till(browser,"name","q"):
		# search_text(browser,"tesla",True,(2017,))
		# search_text(browser,"tesla",True,(2019,))
		# link = search_text(browser,"tesla",True,("any date",))
		list_url = parser_link_post(browser,"https://mbasic.facebook.com/search/posts/?q=tesla&epa=FILTERS&filters=eyJycF9hdXRob3IiOiJ7XCJuYW1lXCI6XCJtZXJnZWRfcHVibGljX3Bvc3RzXCIsXCJhcmdzXCI6XCJcIn0iLCJycF9jcmVhdGlvbl90aW1lIjoie1wibmFtZVwiOlwiY3JlYXRpb25fdGltZVwiLFwiYXJnc1wiOlwie1xcXCJzdGFydF95ZWFyXFxcIjpcXFwiMjAxOVxcXCIsXFxcInN0YXJ0X21vbnRoXFxcIjpcXFwiMjAxOS0wMVxcXCIsXFxcImVuZF95ZWFyXFxcIjpcXFwiMjAxOVxcXCIsXFxcImVuZF9tb250aFxcXCI6XFxcIjIwMTktMTJcXFwifVwifSJ9",20)
		with open("list.txt","a") as f:
			for url in list_url:
				parsed = urlparse.urlparse(url)
				f.write(url)
				f.write("\n")
				f.write(str(parse_qs(parsed.query)))
				f.write("\n")
			
	return browser

if __name__ == '__main__':
	test()