from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import requests

import datetime
import json
import base64

import MySQLdb

def connect():
    conn=MySQLdb.connect(host='stop-looking',user='looking-at',passwd='personal-stuff')
    cursor = conn.cursor()
    cursor.execute('use sandeshghanta$userdata')
    return conn,cursor

def sendMessage(chatId,message,bot_token="go-away-you-creep"):
    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&disable_web_page_preview=true&parse_mode=Markdown"
    r = requests.get(url)
    result = json.loads(r.text)
    if (result['ok']):
        return
    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message+"&disable_web_page_preview=true"
    r = requests.get(url)

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
def clean(x):
    x = str(x)
    if (len(x) == 1):
        x = '0' + x
    return x

def getDays():
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    now = datetime.datetime.now()
    today = now.strftime("%a")
    today_index = days.index(today)
    yesterday_index = (today_index - 1)%7
    yesterday = days[yesterday_index]
    return [today,yesterday]

def isurl(text):
    flags = ['www','http','https','.com','.org','.in']
    if (text.find(" ") != -1):      #A url is not supposed to have spaces in between
        return False
    for flag in flags:
        if (text.find(flag) != -1):
            return True
    return False

def cleanmail(data):
    days = getDays()
    std_text = """You received this message because you are subscribed to the Google Groups "FOSS-2017" group."""
    for mail in data:
        data[mail] = data[mail][:data[mail].find("On " + days[0]+ ",")]
        data[mail] = data[mail][:data[mail].find("On " + days[1]+ ",")]
        data[mail] = data[mail][:data[mail].find(std_text)]
    return data
    '''
    This is for the next release this code is supposed to make inline url's by identifying urls in the text
    for mail in data:
        while (data[mail].find('<') != -1):
            start = data[mail].find('<')
            end = data[mail].find('>')
    return data'''

def getDate():
    now = datetime.datetime.now()
    date = clean(now.day-4) + "-" + clean(now.month) + "-" + clean(now.year)
    return date
    
def getThreadName():
    date = getDate()
    name = "[foss-2017] Status Update "+"["+date+"]"
    return name

def getdata():
    store = file.Storage('whereamI.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('nofile.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    threadName = getThreadName()
    user_id = "me"
    threads = service.users().threads().list(userId=user_id).execute().get('threads', [])
    for thread in threads:
        tdata = service.users().threads().get(userId=user_id, id=thread['id'],format = "full").execute()
        nmsgs = len(tdata['messages'])
        msg = tdata['messages'][0]['payload']
        subject = ''
        for header in msg['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
                break
        data = {}
        if subject == threadName:
            for msg in tdata['messages']:
                emailid = ''
                for header in msg['payload']['headers']:
                    if (header['name'] == "From"):
                        start = header['value'].find('<')
                        end = header['value'].find('>')
                        emailid = header['value'][start+1:end]
                try:
                    content = ""
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == "text/plain":
                            encoded_data = part['body']['data']
                            encoded_data = encoded_data.replace('-','+')        #This is because the encoded_data is encoded in url_safe mode in which encoding is slightly different compared to normal base64 encoding
                            encoded_data = encoded_data.replace('_','/')
                            content = content + base64.b64decode(encoded_data).decode('utf-8')
                        '''if part['mimeType'] == "text/html":
                            encoded_data = part['body']['data']
                            encoded_data = encoded_data.replace('-','+')
                            encoded_data = encoded_data.replace('_','/')
                            content = content + base64.b64decode(encoded_data).decode('utf-8')'''
                    data[emailid] = content
                except:
                    #The FOSS automated mail is the only one without 'parts' in the msg. This is because it does not contain any content in the MIME format. All the user send messages are in MIME format
                    print("FOSS MAIL")
            return data
if __name__ == '__main__':
    data = getdata()
    data = cleanmail(data)
    conn,cursor = connect()
    query = "select * from accepted_users"
    cursor.execute(query)
    accepted_users = cursor.fetchall()
    for user in accepted_users:
        query = "select following from user where chatId = '{0}'".format(user[0])
        cursor.execute(query)
        following = cursor.fetchall()[0][0]
        following = following.strip()
        if (following == ""):
            continue
        following = following.split(' ')
        for usr in following:
            message = ""
            if (usr in data):
                message = "Status update of " + usr + " for the day " + getDate() + '\n\n'
                message = message + data[usr]
            else:
                message = usr + " Did not send a status update for the day " + getDate() + '\n'
            sendMessage(user[0],message)
