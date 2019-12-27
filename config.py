from datetime import datetime

# profile 
LOGIN = "Your login"
PASSWORD = "Your password"
WEBDRIVER_TYPE = 'firefox'

debug = True

# database
send_db = False
db = {
  'user': 'user db',
  'password': 'password db',
  'host': 'host db',
  'database': 'name db',
  'raise_on_warnings': True
}
# request
instance = "request db"

# post
filter_post_publick = True
filter_post_any = True

max_count_comment = 10
max_count_post_from_user = 30
max_count_post_from_search = 10
count_post_iterable = 7

# other
https = "https://"
f_link = "facebook.com"
m_f_link = "mbasic.facebook.com"
LOGIN_REQUIRED = True
LOGIN_URL = "https://facebook.com/login/"
YEAR_NOW = 2019