from flask import Flask, request, abort, Response
import requests
import json
import MySQLdb

app = Flask(__name__)

def connect():
    conn=MySQLdb.connect(host='stop',user='looking-at',passwd='personal-stuff')
    cursor = conn.cursor()
    cursor.execute('use sandeshghanta$userdata')
    return conn,cursor

def isadmin(chatId):
    query = "select * from admin where chatId = '{0}'".format(chatId)
    conn,cursor = connect()
    result = cursor.execute(query)
    if (result > 0):
        return True
    return False

def exists_in_db(chatId):
    conn,cursor = connect()
    query = "select * from user where chatId = '" + chatId + "';"
    result = cursor.execute(query)
    conn.commit()
    if (result > 0):
        return True
    return False

def addEntry(request_data):
    conn,cursor = connect()
    chatId = str(request_data['message']['chat']['id'])
    try:
        nullstr = ""
        query = "insert into user(chatId,following) values ('{0}','{1}');".format(chatId,nullstr)
        cursor.execute(query)
        conn.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)

def get_pending_requests(chatId):
    conn,cursor = connect()
    query = "select * from pending_requests"
    cursor.execute(query)
    requests = cursor.fetchall()
    message = str(len(requests)) + " pending requests\n"
    for request in requests:
        message = message + request[3] + '\n'
    sendMessage(chatId,message)

def check_validity(new_following):
    for mail in new_following:
        if (" " in mail and mail != " "):
            return False,mail + " is not valid"
    new_following = list(filter((" ").__ne__, new_following))   #removing all space emails
    new_following = list(filter(('').__ne__, new_following))    #removing all blank emails
    return True,"All emails are valid"

def sendMessage(chatId,message,bot_token="get-lost-you-stalker"):
    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+chatId+"&text="+message
    requests.get(url)

def get_following(chatId):
    conn,cursor = connect()
    query = "select following from user where chatId = '" + chatId + "';"
    try:
        cursor.execute(query)
        following = list(cursor.fetchall()[0][0].split(' '))   #must convert to list format
        following = list(filter(('').__ne__, following))    #removes all '' from following
        return True,following
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        return False,[]

def isvalidmail(mailid):
    conn,cursor = connect()
    query = "select * from mails where mail_id = '" + mailid + "';"
    result = cursor.execute(query)
    if (result > 0):
        return True
    return False

def follow(chatId,new_following):
    new_following = list(set(new_following))
    if (len(new_following) == 0):
        message = "No input given\n"
        sendMessage(chatId,message)
        return
    valid,message = check_validity(new_following)
    conn,cursor = connect()
    if (not valid):
        sendMessage(chatId,message)
        return
    valid,following = get_following(chatId)
    if (not valid):
        send_error_message(chatId)
        return
    already_following = []
    invalid_mail = []
    addedmail = []
    changes_made = False
    for mail in new_following:
        if (mail not in following):
            if (isvalidmail(mail)):
                changes_made = True
                following.append(mail)
                addedmail.append(mail)
            else:
                invalid_mail.append(mail)
        else:
            already_following.append(mail)
    try:
        query = "update user set following = '" + ' '.join(following) + "' where chatId = '" + chatId + "'"
        cursor.execute(query)
        if (changes_made):
            message = "Your preferences have been updated\n"
        else:
            message = "No changes have been made\n"
        if (len(addedmail) > 0):
            message = message + "You are now also following\n"
            for mail in addedmail:
                message = message + "   -> " +mail + '\n'
        if (len(already_following) > 0):
            message = message + "You were already following\n"
            for mail in already_following:
                message = message + "   -> " +mail + '\n'
        if (len(invalid_mail) > 0):
            message = message + "The following mails do not exist in the database\n"
            for mail in invalid_mail:
                message = message + "   -> " + mail + '\n'
        conn.commit()
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)

def send_error_message(chatId):
    sendMessage(chatId,"Some error happened! Please contact Admin")

def unfollow(chatId,new_following):
    new_following = list(set(new_following))
    if (len(new_following) == 0):
        message = "No input given\n"
        sendMessage(chatId,message)
        return
    valid,message = check_validity(new_following)
    conn,cursor = connect()
    if (not valid):
        sendMessage(chatId,message)
        return
    valid,following = get_following(chatId)
    if (not valid):
        send_error_message(chatId)
        return
    not_following = []
    invalid_mail = []
    removedmails = []
    changes_made = False
    for mail in new_following:
        if (mail in following):
            changes_made = True
            following.remove(mail)
            removedmails.append(mail)
        else:
            if (isvalidmail(mail)):
                not_following.append(mail)
            else:
                invalid_mail.append(mail)
    try:
        query = "update user set following = '" + ' '.join(following) + "' where chatId = '" + chatId + "'"
        cursor.execute(query)
        if (changes_made):
            message = "Selected Emails have been successfully dropped\n"
        else:
            message = "No changes made\n"
        if (len(removedmails) > 0):
            message = message + "You are no longer following\n" 
            for mail in not_following:
                message = message + "   -> " + mail + '\n'
        if (len(not_following) > 0):
            message = message + "You were not following the following mails\n" 
            for mail in not_following:
                message = message + "   -> " + mail + '\n'
        if (len(invalid_mail) > 0):
            message = message + "The following mails do not exist in the database\n"
            for mail in invalid_mail:
                message = message + "    -> " +mail + '\n'
        conn.commit()
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)

def unfollow_all(chatId):
    conn,cursor = connect()
    try:
        query = "update user set following = ' ' where chatId = '" + chatId + "'"
        cursor.execute(query)
        message = "Unfollowed all users\n"
        conn.commit()
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)

def list_following(chatId):
    try:
        valid,following = get_following(chatId)
        if (not valid):
            send_error_message(chatId)
            return
        if (len(following) == 0):
            message = "You are currently not following anyone\n"
        else:
            message = "You are currently following\n"
            for mail in following:
                message = message +"    -> " +mail + '\n'
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)
        
def revoke_access(chatId,usernames):
    usernames = list(set(usernames))
    conn,cursor = connect()
    revoked_for = []
    for user in usernames:
        cId = ""
        granted = False
        requesting = False
        message = ""
        try:
            query = "select chatId from accepted_users where tusername = '{0}'".format(user)
            result = cursor.execute(query)
            if (result > 0):
                granted = True
                cId = cursor.fetchall()[0][0]
                revoked_for.append(user)
                query = "delete from accepted_users where tusername = '{0}'".format(user)
                cursor.execute(query)
            query = "select chatId from pending_requests where tusername = '{0}'".format(user)
            result = cursor.execute(query)
            if (result > 0):
                requesting = True
                cId = cursor.fetchall()[0][0]
                revoked_for.append(user)
                query = "delete from pending_requests where tusername = '{0}'".format(user)
                cursor.execute(query)
            conn.commit()
            if (granted and not requesting):
                message = "Your access has been removed by the Admin\n"
            if (requesting and not granted):
                message = "Your request has been cancelled by the Admin\n"
            if (requesting and granted):
                message = "Your access has been removed\n"
                sendMessage(chatId,"Data Redundancy in the server database!!!!")
            if (granted or requesting):
                sendMessage(cId,message)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            send_error_message(chatId)
            return
    revoked_for = list(set(revoked_for))
    message = ""
    if (len(revoked_for) > 0):
        message = "Access has been revoked for \n"
        for user in usernames:
            message = message + "     -> " + user + '\n'
    else:
        message = "No valid users to revoke access"
    sendMessage(chatId,message)
    
def list_all_mails(chatId):
    conn,cursor = connect()
    cursor.execute("select * from mails")
    result = cursor.fetchall()
    mails = [x[0] for x in result]
    message = "The available mails are \n"
    for mail in mails:
        message = message + " ->" + mail + '\n'
    sendMessage(chatId,message)
    
def request_access(request_data):
    conn,cursor = connect()
    chatId = str(request_data['message']['chat']['id'])
    firstName = request_data['message']['chat']['first_name']
    lastName = request_data['message']['chat']['last_name']
    tusername = request_data['message']['from']['username']
    message = ""
    try:
        query = "select * from pending_requests where chatId = {0}".format(chatId)
        result = cursor.execute(query)
        if (result > 0):
            message = "You have already requested for access. Please wait patiently the admin will soon accept your request\n"
        else:
            query = "select * from accepted_users where chatId = {0}".format(chatId)
            result = cursor.execute(query)
            if (result > 0):
                message = "You already have access\n"
            else:
                query = "insert into pending_requests (chatId,firstName,lastName,tusername) values ('{0}','{1}','{2}','{3}');".format(chatId,firstName,lastName,tusername)
                cursor.execute(query)
                conn.commit()
                message = "The admin will be notified about your request to use this bot. Once he accepts it you will be able to get emails. You can keep modifiying your preferences till then"
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)
    
def grant_access(chatId,usernames):
    usernames = list(set(usernames))
    if (len(usernames) == 0):
        message = "No input given\n"
        sendMessage(chatId,message)
        return
    conn,cursor = connect()
    query = "select * from pending_requests"
    cursor.execute(query)
    pending_requests = cursor.fetchall()
    query = "select tusername from accepted_users"
    cursor.execute(query)
    accepted_users = cursor.fetchall()
    conn.commit()
    accepted_users = [x[0] for x in accepted_users]
    toaccept = []
    alreadydone = []
    invalid_handle = []
    for user in usernames:
        flag = False
        for request in pending_requests:
            if (request[3] == user):
                toaccept.append(request)
                flag = True
                break
        if (not flag):
            if (user in accepted_users):
                alreadydone.append(user)
            else:
                invalid_handle.append(user)
    try:
        message = ""
        if (len(toaccept) > 0):
            for row in toaccept:
                query = "insert into accepted_users (chatId,firstName,lastName,tusername) values ('{0}','{1}','{2}','{3}')".format(row[0],row[1],row[2],row[3])
                cursor.execute(query)
            conn.commit()
            for row in toaccept:
                query = "delete from pending_requests where chatId = {0}".format(row[0])
                cursor.execute(query)
            conn.commit()
            for row in toaccept:
                message = "Congratulation's you are granted access to use this bot!!!!"
                sendMessage(row[0],message)
            message = "granted access to\n"
            for row in toaccept:
                message = message + "   ->" + row[3] +'\n'
        else:
            message = "No changes done\n"
        if (len(alreadydone) > 0):
            message = message + "The following users already have access\n"
            for user in alreadydone:
                message = message + "   ->" + user + '\n'
        if (len(invalid_handle) > 0):
            message = message + "The following users either have not requested for access or they do not exist in our database\n"
            for user in invalid_handle:
                message = message + "   ->" + user + '\n'
        conn.commit()
        sendMessage(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        send_error_message(chatId)

def convert(message):
    index = 0
    message = message.strip()
    newmessage = ""
    while (index < len(message)):
        if (message[index] == ' '):
            break
        else:
            newmessage = newmessage + message[index].lower()
        index = index + 1
    newmessage = newmessage + message[index:]
    return newmessage

def add_mail(chatId,mails):
    mails = list(set(mails))
    conn,cursor = connect()
    already_exist = []
    added_mail = []
    for mail in mails:
        try:
            if (isvalidmail(mail)):
                already_exist.append(mail)
            else:
                query = "insert into mails (mail_id) values ('{0}');".format(mail)
                cursor.execute(query)
                conn.commit()
                added_mail.append(mail)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            print (e)
            send_error_message(chatId)
    message = "No changes done\n"
    if (len(added_mail) > 0):
        message = "Inserted the following into the database\n"
        for mail in added_mail:
            message = message + "   ->" + mail + '\n'
    if (len(already_exist)):
        message = message + "The following already exist in the database\n"
        for mail in already_exist:
            message = message + "   ->" + mail
    sendMessage(chatId,message)
    return

def remove_mail(chatId,mails):
    mails = list(set(mails))
    conn,cursor = connect()
    not_present = []
    removed_mail = []
    for mail in mails:
        try:
            if (isvalidmail(mail)):
                query = "delete from mail where mail_id = '{0}';".format(mail)
                cursor.execute(query)
                conn.commit()
                removed_mail.append(mail)
            else:
                not_present.append(mail)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            send_error_message(chatId)
            return
    message = "No changes done\n"
    if (len(removed_mail) > 0):
        message = "Deleted the following from the database\n"
        for mail in removed_mail:
            message = message + "   ->" + mail + '\n'
    if (len(not_present)):
        message = message + "The following do not exist in the database\n"
        for mail in not_present:
            message = message + "   ->" + mail + '\n'
    sendMessage(chatId,message)
    return

def sendhelp(request_data):
    chatId = str(request_data['message']['chat']['id'])
    firstName = request_data['message']['chat']['first_name']
    lastName = request_data['message']['chat']['last_name']
    message = """Hello Welcome to the Status Update Bot!
It is great to see you here {0} {1}
Everyday you wish to see the status updates of some people let it be your mentee/mentor. But searching for that particular mail is difficult in the thread\n
This bot helps you with that. All you have to do is to 'follow' whosever updates you want to get. This bot will send you their status updates to via telegram chat!\n
The methods which are accessable to you are
1) /follow: Using this command you can follow others. You can give multiple email id's at once(space seperated).
    Ex: /follow mail1
    Ex: /follow mail1 mail2
                
2) /unfollow: Using this command you can unfollow a person whom you are following. You can give multiple email id's at once(space seperated).
    Ex: /unfollow mail1
    Ex: /unfollow mail1 mail2
            
3) /unfollow_all: Using this command you can unfollow all the people whom you are currently following. This command takes no arguments
    Ex: /unfollow_all
            
4) /list_following: Lists all the people whom you are currently following. This command takes no arguments
    Ex: /list_following

5) /list_all_mails: Lists all the mails in the FOSS'17 group. This command takes no arguments
    Ex: /list_all_mails
            
6) /request_access: Requests the admin to grant you access to recieve mail. This command takes no arguments
    Ex: /request_access

7) /help: Displays this message
    Ex: /help
    
*NOTE*: This is a public bot. To make sure that the wrong people do not get the status updates of the FOSS mailing list you are required to request access from the admin. All you have to do is send the /request_access command. Until the admin accepts your request you will not be getting the status updates of others. But you can keep editing your preferences till then i.e you can add whom to follow and not. Once the admin accepts your request you will be getting a notification. Similary the admin can revoke your access at any point of time.
You will be recieving the status updates of the previous day daily at 5:10 AM
Please check if your mail is present in /list_all_mails if not please do ping me at sghanta05@gmail.com or 8137069878""".format(firstName,lastName)
    sendMessage(chatId,message)
    return

def handle_request(request_data):
    message = request_data['message']['text']
    chatId = str(request_data['message']['chat']['id'])
    message = convert(message)
    if (message.startswith('/start') or message.startswith('/help')):
        sendhelp(request_data)
    elif (message.startswith('/follow')):
        if (len(message) > 8):
            emails = list(message[8:].split(' '))
            follow(chatId,emails)
        else:
            message = "The /follow command requires some input to be given"
            sendMessage(chatId,message)
    elif (message.startswith('/unfollow')):
        if (len(message) > 10):
            emails = list(message[10:].split(' '))
            unfollow(chatId,emails)
        else:
            message = "The /unfollow command requires some input to be given"
            sendMessage(chatId,message)
    elif (message.startswith('/unfollow_all')):
        unfollow_all(chatId)
    elif (message.startswith('/list_following')):
        list_following(chatId)
    elif (message.startswith('/request_access')):
        request_access(request_data)
    elif (message.startswith('/list_all_mails')):
        list_all_mails(chatId)
    elif (isadmin(chatId)):
        if (message.startswith('/get_pending_requests')):
            get_pending_requests(chatId)
        elif (message.startswith('/grant_access ')):
            usernames = list(message[14:].split(' '))
            grant_access(chatId,usernames)
        elif (message.startswith('/revoke_access ')):
            usernames = list(message[15:].split(' '))
            revoke_access(chatId,usernames)
        elif (message.startswith('/add_mail ')):
            mails = list(message[10:].split(' '))
            add_mail(chatId,mails)
        elif (message.startswith('/remove_mail ')):
            mails = list(message[13:].split(' '))
            remove_mail(chatId,mails)
        else:
            message = "Invalid input"
            sendMessage(chatId,message)
    else:
        message = "Invalid Input"
        sendMessage(chatId,message)

@app.route('/', methods=['GET','POST'])
def webhook():
    request_data = request.get_json()
    chatId = str(request_data['message']['chat']['id'])
    if (not exists_in_db(chatId)):
        addEntry(request_data)
    handle_request(request_data)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0',port="1234")
