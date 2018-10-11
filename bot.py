import requests
import json


values = {}
with open("values.json","r") as file:
    values = json.load(file)

def send_message(chatId,message,disable_web_page_preview=False,send_formatted=True,bot_token=values['bot_token']):
    if (send_formatted):
        url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&parse_mode=markdown&disable_web_page_preview="+str(disable_web_page_preview)
        r = requests.get(url)
        result = json.loads(r.text)
        if (result['ok']):
            return
    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&disable_web_page_preview="+str(disable_web_page_preview)
    requests.get(url)

def send_admin_message(message):
    from database import connect    #This import is placed here to avoid circular dependency
    conn,cursor = connect()
    query = "select chatId from admin"
    cursor.execute(query)
    adminId = cursor.fetchall()[0][0]
    conn.close()
    send_message(adminId,message)

def send_error_message(chatId):
    send_message(chatId,"Some error happened! Please contact Admin")

def send_message_to_all(message):
    from database import connect    #This import is placed here to avoid circular dependency
    conn,cursor = connect()
    query = "select chatId from user"
    cursor.execute(query)
    chatIds = cursor.fetchall()
    for chatId in chatIds:
        send_message(chatId[0],message)
    conn.close()

def reset_webhook(chatId):
    #There is something wrong in this method have to fix it later
    '''url = "api.telegram.org/bot{0}/deleteWebhook".format(values['bot_token'])
    r = requests.get(url)
    url = "api.telegram.org/bot{0}/setWebhook?url=sandeshghanta.pythonanywhere.com/{1}".format(values['bot_token'],values['bot_token'])
    r = requests.get(url)
    message = "Reset the webhook"
    send_message(chatId,message)'''
    do_nothing = 1
