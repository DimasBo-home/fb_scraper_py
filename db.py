
from methods import replace_link
import config as settings

def is_send(func):
	def wrapper(arg1,arg2 = True):
		if settings.send_db:
			print("request db")
			func(arg1,arg2)
	return wrapper

def get_request(instance):
	try:
		mydb = mysql.connector.connect(**settings.db)
		mycursor = mydb.cursor()
		
		mycursor.execute('SELECT request  FROM pipeline  WHERE instance = %s ORDER BY id', [instance])
		myresult = mycursor.fetchall()[0]
		request_id = myresult[0]
		
		print('request_id:',request_id)
		mycursor.execute('SELECT text_id, date FROM request_date WHERE id = %s ORDER BY id ', [request_id])
		myresult = mycursor.fetchall()[0]
		request_text_id = myresult[0]
		request_date = myresult[1]
		print('request_date:',request_date)

		mycursor.execute('SELECT text FROM request_text WHERE id = %s ORDER BY id ', [request_text_id])
		myresult = mycursor.fetchall()[0]
		request_text = myresult[0]
		print('request_text:',request_text)
		mydb.close()
		if request_date:
			return {"request_text":request_text,"request_date":request_date.date()}
		return {"request_text":request_text}

	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))

@is_send
def request_list_search(request,list_result):
	data_old = None
	try:
		mydb = mysql.connector.connect(**settings.db)
		mycursor = mydb.cursor()
			
		sql = 'INSERT INTO `fb_search_result`(`request`, `url`, `post_id`, `user_id`, `type`) VALUES (%s,%s,%s,%s,%s)'
		for data in list_result:
			print
			r = ( request['request_text'] + " " + request['request_date'].strftime("%Y-%m") ) if "request_date" in request else request['request_text'] 
			var = (r,replace_link(data['url']),data['post_id'],data['actor_id'], data['type'])
			mycursor.execute(sql, var)
			data_old = var

		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
		mydb.close()
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))
		print(data_old)

@is_send
def request_list_user(user_id,list_result):
	data_old = None
	try:
		mydb = mysql.connector.connect(**settings.db)
		mycursor = mydb.cursor()
		
		sql = 'INSERT INTO `fb_user_result`(`type`,`user_id`, `post_id`,`url`) VALUES (%s,%s,%s,%s)'
		for data in list_result:
			var = (data['type'],user_id,data['post_id'],replace_link(data['url']))
			mycursor.execute(sql, var)
			data_old = var
		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
		mydb.close()
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))
		print(data_old)

@is_send
def request_data(data,is_user=True):
	try:
		mydb = mysql.connector.connect(**settings.db)
		mycursor = mydb.cursor()
		
		sql_post = 'INSERT INTO `fb_posts`(`post_id`, `user_id`, `url`, `description`, `img`, `date`, `likes`, `shares`, `comments`) VALUES (%s,%s,%s, %s,%s,%s, %s,%s,%s)'
		var_post = (data['post_id'],data['actor_id'],replace_link(data['url']), data['content']['description'],replace_link(data['content']['img']),data['content']['date'], data['likes'],data['shares'],data['comment_count'])
		mycursor.execute(sql_post,var_post)
		if is_user:
			sql_user = 'INSERT INTO `fb_users`( `user_id`,`user_name`,`link_user`) VALUES (%s,%s,%s)'
			var_user = (data['actor_id'],data['content']['username'],replace_link(data['content']['link_user']))
			mycursor.execute(sql_user, var_user)
		sql_comment = 'INSERT INTO `fb_comments`( `post_id`,`user_name`,`acrot_link`,`description`,`replies_link`) VALUES (%s,%s,%s, %s,%s)'
		for comment in data['comments']:
			var_comment = (data['post_id'],comment['username'],replace_link(comment['actor_url']),comment['description'],replace_link(comment['replies_link']))
			mycursor.execute(sql_comment, var_comment)
		mydb.commit()
		print(mycursor.rowcount, "record inserted.")
		mydb.close()
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))