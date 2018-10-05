import requests
import json
from database import connect
def send_message(chatId,message,disable_web_page_preview=False,send_formatted=True,bot_token="676823964:AAGGOPlUffhMlubmIL1SlPtQmaiaLy-rhNQ"):
    if (send_formatted):
        url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&parse_mode=markdown&disable_web_page_preview="+disable_web_page_preview
        r = requests.get(url)
        result = json.loads(r.text)
        if (result['ok']):
            return
    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&disable_web_page_preview="+disable_web_page_preview
    requests.get(url)

def sendAdminMessage(message):
    conn,cursor = connect()
    query = "select chatId from admin"
    cursor.execute(query)
    adminId = cursor.fetchall()[0][0]
    conn.close()
    sendMessage(adminId,message)

def send_error_message(chatId):
    sendMessage(chatId,"Some error happened! Please contact Admin")

def send_message_to_all(message):
    conn,cursor = connect()
    query = "select chatId from user"
    cursor.execute(query)
    chatIds = cursor.fetchall()
    for chatId in chatIds:
        sendMessage(chatId[0],message)
    conn.close()

def reset_webhook(chatId):
    '''url = "api.telegram.org/bot676823964:AAGGOPlUffhMlubmIL1SlPtQmaiaLy-rhNQ/deleteWebhook"
    r = requests.get(url)
    url = "api.telegram.org/bot676823964:AAGGOPlUffhMlubmIL1SlPtQmaiaLy-rhNQ/setWebhook?url=sandeshghanta.pythonanywhere.com/676823964:AAGGOPlUffhMlubmIL1SlPtQmaiaLy-rhNQ"
    r = requests.get(url)
    message = "Reset the webhook"
    sendMessage(chatId,message)'''
    do_something = 1
    #There is something wrong in this method have to fix it later
