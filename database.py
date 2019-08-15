from bot import send_error_message
import MySQLdb
import json

values = {}
with open("/home/sandeshghanta/mysite/values.json","r") as file:
    values = json.load(file)

def connect():
    conn=MySQLdb.connect(host=values['database']['host'],user=values['database']['user'],passwd=values['database']['passwd'])
    #conn=MySQLdb.connect(host='sandeshghanta.mysql.pythonanywhere-services.com',user='sandeshghanta',passwd='onread1.com')
    cursor = conn.cursor()
    cursor.execute('use {0}'.format(values['database']['dbname']))
    return conn,cursor

def isadmin(chatId):
    try:
        query = "select * from admin where chatId = '{0}'".format(chatId)
        conn,cursor = connect()
        result = cursor.execute(query)
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)
        return False    #Added for safety reasons. For any reason if the query does not execute as expected. The answer should be False
    if (result > 0):
        return True
    return False

def exists_in_db(chatId):
    conn,cursor = connect()
    query = "select * from user where chatId = '" + chatId + "';"
    try:
        result = cursor.execute(query)
        conn.commit()
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)
    if (result > 0):
        return True
    return False

def add_entry_to_user_in_db(request_data):
    conn,cursor = connect()
    chatId = str(request_data['message']['chat']['id'])
    try:
        nullstr = ""
        query = "insert into user(chatId,following) values ('{0}','{1}');".format(chatId,nullstr)
        cursor.execute(query)
        conn.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)
    conn.close()
