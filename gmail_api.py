from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import requests
from date_methods import get_today_date, get_days_in_words
from bot import send_message
from database import connect
import MySQLdb
import datetime
import json
import base64

with open("values.json","r") as file:
    values = json.load(file)

def cleanmail(data):
    days = get_days_in_words()
    std_text = """You received this message because you are subscribed to the Google Groups "FOSS-2017" group."""
    for mail in data:
        index = data[mail].find("On " + days[0]+ ",")
        if (index != -1):
            data[mail] = data[mail][:index]
        index = data[mail].find("On " + days[1]+ ",")
        if (index != -1):
            data[mail] = data[mail][:index]
        index = data[mail].find("On " + days[2]+ ",")
        if (index != -1):
            data[mail] = data[mail][:index]
        index = data[mail].find(std_text)
        if (index != -1):
            data[mail] = data[mail][:index]
    return data
    '''
    This is for the next release this code is supposed to make inline url's by identifying urls in the text
    for mail in data:
        while (data[mail].find('<') != -1):
            start = data[mail].find('<')
            end = data[mail].find('>')
    return data'''

def send_mails_to_users(data,date):
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
                message = "Status update of " + usr + " for the day " + date + '\n\n'
                message = message + data[usr]
            else:
                message = usr + " Did not send a status update for the day " + date + '\n'
            send_message(user[0],message,True)
    conn.close()

def list_messages_matching_query(service, user_id, query=''):
    response = service.users().messages().list(userId=user_id,q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
    else:
        return []
    message = service.users().messages().get(userId="me", id=messages[0]['id'],format='metadata').execute()
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages.extend(response['messages'])
    return messages

def get_sender_email_id_and_maildata(service, user_id, msg_id):
    email_id = ''
    msg = service.users().messages().get(userId=user_id, id=msg_id,format='full').execute()
    header_data = msg["payload"]["headers"]
    sender_text = "X-Original-Sender"
    sender_text = "From"
    for data in header_data:
        if sender_text in data["name"]:
            email_id = data["value"]
            if (email_id.find('<') != -1 and email_id.find('>') != -1):     #The email_id is in the format <sghanta05@gmail.com>
                email_id = email_id[email_id.find('<')+1 : email_id.find('>')]
    content = ""
    try:
        for part in msg['payload']['parts']:
            if part['mimeType'] == "text/plain":
                encoded_data = part['body']['data']
                encoded_data = encoded_data.replace('-','+')        #This is because the encoded_data is encoded in url_safe mode in which encoding is slightly different compared to normal base64 encoding
                encoded_data = encoded_data.replace('_','/')
                content = content + base64.b64decode(encoded_data).decode('utf-8')
    except:
        #The FOSS automated mail is the only one without 'parts' in the msg. This is because it does not contain any content in the MIME format. All the user send messages are in MIME format
        print("FOSS MAIL")
    return (email_id,content)

def getdata(date):
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    threadName = '[foss-2017] Status Update [' + date + ']'
    user_id = "me"
    messages = list_messages_matching_query(service, user_id='me', query=threadName)
    email_to_content = {}
    for message in messages:
        email_id,content = get_sender_email_id_and_maildata(service, user_id="me", msg_id=message['id'])
        email_to_content[email_id] = content
    return email_to_content

def convert_to_json_and_store(mails_list,filename):
    filename = filename.replace('2018','18')    #HAVE TO REWRITE THE CODE
    filename = filename.replace('2019','19')
    data = {}   #Initializing data as an empty dictionary and then adding all the batches as keys
    for batch in values['batches']:
        data[batch] = []
    fileobj = open('maildata.json','r')
    mails_data = json.load(fileobj)
    fileobj.close()
    for mail in mails_list:
        in_batch = False
        for batch in values['batches']:
            if (mail in mails_data[batch]):
                in_batch = True
                data[batch].append(mail)
                break
        if (not in_batch):
            #ONLY the amritapurifoss mail is supposed to be printed. If any other mail is being printed then it means that the mail is not there in maildata.json and must be added!!
            app.logger.info("The following mail was not there in the database " + mail)

    if (len(data['2015']) == 0 and len(data['2016']) == 0 and len(data['2017']) == 0):
        return
    file = open("jsondata/"+filename+".txt",'w+')
    json.dump(data,file)
    file.close()

if __name__ == '__main__':
    date = get_today_date()
    #The returned date will be in the format dd-mm-yy
    #We need the format to be dd-mm-yyyy
    date = date[:-2] + "2018"
    print ("Currently at " + date)
    email_to_content = getdata(date)
    if (email_to_content != {}):
        #Send the mails iff the status update thread has been initiated
        emails = [key for key in email_to_content]
        convert_to_json_and_store(emails,date)
        send_mails_to_users(email_to_content,date)
