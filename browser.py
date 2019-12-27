import config as settings
from methods import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import platform
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# WebDriverWait(driver, 1000000).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[3]/div/button/span'))).click()

def formater_url(url):
	return url.split("?")[0]

def remove_element(browser,element):
	try:
		browser.execute_script("""
var element = arguments[0];
element.parentNode.removeChild(element);
""", element)
	except:
		print("falata remove element", element)
def remove_elements(browser,elements):
	for element in elements:
		remove_element(browser,element)
def open_link(browser,url):
	try:
		browser.get(url)
	except Exception as e:
		print("E : open browser " + url )

def get_login_credentials():
	try:
		username = settings.LOGIN
		password = settings.PASSWORD

		return username, password
	except Exception as e:
		print("input login or password in config")
		return None, None

def login_():
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
		return browser

def find_element(browser, key, value):
	if key == 'id':
		try:
			return browser.find_element_by_id(value)
		except NoSuchElementException:
			print("There is no such exception to the \"id\" element ", value)
	elif key == "css":
		try:
			return browser.find_element_by_css_selector(value)
		except NoSuchElementException:
			print("There is no such exception to the \"css selector\" element", value)
	elif key == 'name':
		try:
			return browser.find_element_by_name(value)
		except NoSuchElementException:
			print("There is no such exception to the \" xpath\" element", value)
	elif key == 'xpath':
		try:
			return browser.find_element_by_xpath(value)
		except NoSuchElementException:
			print("There is no such exception to the \" xpath\" element", value)
	elif key == "tag":
		try:
			return browser.find_element_by_tag_name(value)
		except NoSuchElementException:
			print("There is no such exception to the \"tag\" element ", value)
	elif key == "class":
		try:
			return browser.find_element_by_class_name(value)
		except NoSuchElementException:
			print("There is no such exception to the \"class\" element ", value)
	return None

def find_back_a(el):
	while el.tag_name != 'a':
		el = back_el(el)
	return el

def back_el(el):
	try:
		return find_element(el,"xpath",'..')
	except:
		print("[F:to bakc does not element]")
		return None

def find_elements(browser, key, value):
	if key == 'css':
		try:
			return browser.find_elements_by_css_selector(value)
		except NoSuchElementException:
			print("There is no such exception to the \"css selector\" element", value)
	elif key == 'xpath':
		try:
			return browser.find_elements_by_xpath(value)
		except NoSuchElementException:
			print("There is no such exception to the \" xpath\" element", value)
	elif key == "class":
		try:
			return browser.find_elements_by_class(value)
		except NoSuchElementException:
			print("There is no such exception to the \"id\" element ", value)
	elif key == "tag":
		try:
			return browser.find_elements_by_tag_name(value)
		except NoSuchElementException:
			print("There is no such exception to the \"id\" element ", value)
	return None

def send_keys(elements, submit=False):

	"""
	Enter given keys to form elements in webpage
	:param elements: WebElements
	:param submit: submit flag. if True, form will be submitted after entering keys
	:return: None
	"""

	final_element = None
	for each_element in elements:
		each_element['element'].send_keys(each_element['value'])
		final_element = each_element

	if submit:
		final_element['element'].submit()

def not_wait_till(browser,element):
	try:
		wait = WebDriverWait(browser, 10)
		wait.until(EC.staleness_of(element))
		return True
	except Exception as e:
		pass
	return False

def is_element(browser, key, value):
	if key == 'id':
		try:
			browser.find_element_by_id(value)
			return True
		except NoSuchElementException:
			pass
	elif key == "css":
		try:
			browser.find_element_by_css_selector(value)
			return True
		except NoSuchElementException:
			pass
	elif key == 'name':
		try:
			browser.find_element_by_name(value)
			return True
		except NoSuchElementException:
			pass
	elif key == 'xpath':
		try:
			browser.find_element_by_xpath(value)
			return True
		except NoSuchElementException:
			pass
	elif key == "tag":
		try:
			browser.find_element_by_tag_name(value)
			return True
		except NoSuchElementException:
			pass
	elif key == "class":
		try:
			browser.find_element_by_class_name(value)
			return True
		except NoSuchElementException:
			pass
	return False

def wait_till(browser, key, value):

	"""
	Stop the execution till given element is found in the browser
	:param browser: webdriver instance
	:param key: selector: 'id', 'class', 'xpath'
	:param value: value for the selector
	:return: True if element found, otherwise False
	"""

	try:
		wait = WebDriverWait(browser, 10)

		if key == 'id':
			wait.until(EC.visibility_of_element_located((By.ID, value)))

		elif key == 'name':
			wait.until(EC.visibility_of_element_located((By.NAME, value)))

		elif key == 'class':
			wait.until(EC.visibility_of_element_located((By.CLASS_NAME, value)))

		elif key == 'xpath':
			wait.until(EC.visibility_of_element_located((By.XPATH, value)))

		elif key == 'css':
			wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, value)))
		return True

	except TimeoutException as e:
		print(value	)
		print ("# E: [Find Element] <{error}>".format(error=str(e)))
		return False

def login(browser, username_str, password_str):

	"""
	To login into indeed using given username and password
	:param browser: Webdriver instance
	:param username_str: username for login
	:param password_str: password for login
	:return: browser in logged in state, if successful login, otherwise Null
	"""

	open_link(browser, settings.LOGIN_URL)

	found = wait_till(browser, 'xpath', '//*[@name="email"]')

	""" Logging into our own profile """
	if found:
		login = find_element(browser,"css",'[name="email"]')
		password = find_element(browser,"css",'[name="pass"]')
		send_keys([
			{
				'element': login,
				'value': username_str
			},
			{
				'element': password,
				'value': password_str
			}
		],submit=True)
		# find_element(browser,"css","value='OK'").click()

		# b.find_element_by_css_selector("[type='submit']").click()
		# if submit!=None:
			# submit.click()
		return True
	else:
		print ("E: [Waiting] Timed out waiting for page to load")
		browser.quit()
		return None

def get_browser():

	"""
	Open new webdriver instance and return
	:return: Webdriver instance (Logged in if required)
	"""
	if settings.WEBDRIVER_TYPE == 'firefox':
		profile = FirefoxProfile()
		profile.set_preference("media.volume_scale", "0.0")
		profile.set_preference("media.autoplay.enabled",False)
		profile.set_preference("dom.webnotifications.enabled",False)
		profile.set_preference("dom.push.enabled",False)
		profile.set_preference("datareporting.healthreport.uploadEnabled",False)
		profile.set_preference("browser.safebrowsing.downloads.enabled",False)
		profile.set_preference("browser.safebrowsing.malware.enabled",False)
		profile.set_preference("geo.enabled",False)
		profile.set_preference("geo.wifi.uri","")
		profile.set_preference("extensions.pocket.enabled",False)
		profile.set_preference("browser.aboutHomeSnippets.updateUrl",False)
		profile.set_preference("permissions.default.image",2)
		profile.set_preference("image.animation_mode","none")
		profile.set_preference("intl.accept_languages", "'en-US, en'")
		browser = webdriver.Firefox(profile)
		browser.maximize_window()
		return browser