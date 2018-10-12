# -*- coding: utf-8 -*-
from flask import Flask, request, abort, Response, send_from_directory
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import json
import MySQLdb
import random

from date_methods import clean_arg_for_date, clean_date_for_plot, get_month_for_plot, get_today_date, is_valid_date, is_smaller_than_today
import datetime
import os

from bot import send_message, send_admin_message, send_error_message, send_message_to_all, reset_webhook

from database import connect, isadmin, exists_in_db, add_entry_to_user_in_db

app = Flask(__name__)

def get_pending_requests(chatId):
    conn,cursor = connect()
    query = "select * from pending_requests"
    cursor.execute(query)
    requests = cursor.fetchall()
    message = str(len(requests)) + " pending requests\n"
    for request in requests:
        message = message + request[3] + '\n'
    send_message(chatId,message)

def remove_blank_mails(new_following):      #This method is used to remove all blank mails
    new_following = list(filter((" ").__ne__, new_following))   #removing all space emails
    new_following = list(filter(('').__ne__, new_following))    #removing all blank emails
    return new_following

def get_following(chatId):
    conn,cursor = connect()
    query = "select following from user where chatId = '" + chatId + "';"
    try:
        cursor.execute(query)
        conn.close()
        following = list(cursor.fetchall()[0][0].split(' '))   #must convert to list format
        following = remove_blank_mails(following)
        return True,following
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        conn.close()
        return False,[]

def is_valid_mail(mailid):
    query = "select * from mails where mail_id = '" + mailid + "';"
    try:
        conn,cursor = connect()
        result = cursor.execute(query)
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        conn.close()
    if (result > 0):
        return True
    return False

def follow(chatId,new_following):
    new_following = list(set(new_following))
    if (len(new_following) == 0):
        message = "No input given\n"
        send_message(chatId,message)
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
            if (is_valid_mail(mail)):
                changes_made = True
                following.append(mail)
                addedmail.append(mail)
            else:
                invalid_mail.append(mail)
        else:
            already_following.append(mail)
    try:
        conn,cursor = connect()
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
        conn.close()
        send_message(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        conn.close()

def unfollow(chatId,new_following):
    new_following = list(set(new_following))
    if (len(new_following) == 0):
        message = "No input given\n"
        send_message(chatId,message)
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
            if (is_valid_mail(mail)):
                not_following.append(mail)
            else:
                invalid_mail.append(mail)
    try:
        conn,cursor = connect()
        query = "update user set following = '" + ' '.join(following) + "' where chatId = '" + chatId + "'"
        cursor.execute(query)
        if (changes_made):
            message = "Selected Emails have been successfully dropped\n"
        else:
            message = "No changes made\n"
        if (len(removedmails) > 0):
            message = message + "You are no longer following\n"
            for mail in removedmails:
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
        send_message(chatId,message)
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info()
        send_error_message(chatId)
        conn.close()

def unfollow_all(chatId):
    conn,cursor = connect()
    try:
        query = "update user set following = ' ' where chatId = '" + chatId + "'"
        cursor.execute(query)
        message = "Unfollowed all users\n"
        conn.commit()
        send_message(chatId,message)
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        conn.close()

def list_following(chatId):
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
    send_message(chatId,message)

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
            conn.close()
            if (granted and not requesting):
                message = "Your access has been removed by the Admin\n"
            if (requesting and not granted):
                message = "Your request has been cancelled by the Admin\n"
            if (requesting and granted):
                message = "Your access has been removed\n"
                send_message(chatId,"Data Redundancy in the server database!!!!")
            if (granted or requesting):
                send_message(cId,message)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            app.logger.info(e)
            send_error_message(chatId)
            conn.close()
            return
    revoked_for = list(set(revoked_for))
    message = ""
    if (len(revoked_for) > 0):
        message = "Access has been revoked for \n"
        for user in usernames:
            message = message + "     -> " + user + '\n'
    else:
        message = "No valid users to revoke access"
    send_message(chatId,message)

def list_all_mails(chatId):
    try:
        conn,cursor = connect()
        cursor.execute("select * from mails")
        result = cursor.fetchall()
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        conn.close()
        return
    mails = [x[0] for x in result]
    message = "The available mails are \n"
    for mail in mails:
        message = message + " ->" + mail + '\n'
    send_message(chatId,message)

def request_access(request_data):
    conn,cursor = connect()
    chatId = str(request_data['message']['chat']['id'])
    firstName = ""
    if ('first_name' in request_data['message']['chat']):
        firstName = request_data['message']['chat']['first_name']
    lastName = ""
    if ('last_name' in request_data['message']['chat']):
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
                send_admin_message("You have a pending request from " + tusername)
                message = "The admin will be notified about your request to use this bot. Once he accepts it you will be able to get emails. You can keep modifiying your preferences till then"
        send_message(chatId,message)
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        conn.close()

def grant_access(chatId,usernames):
    usernames = list(set(usernames))
    if (len(usernames) == 0):
        message = "No input given\n"
        send_message(chatId,message)
        return
    try:
        conn,cursor = connect()
        query = "select * from pending_requests"
        cursor.execute(query)
        pending_requests = cursor.fetchall()
        query = "select tusername from accepted_users"
        cursor.execute(query)
        accepted_users = cursor.fetchall()
        conn.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        return
    accepted_users = [x[0] for x in accepted_users]
    toaccept = []
    alreadydone = []
    invalid_handle = []
    for user in usernames:
        flag = False
        for request in pending_requests:
            if (request[3] == user or user == '*'):
                toaccept.append(request)
                flag = True
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
                send_message(row[0],message)
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
        conn.close()
        send_message(chatId,message)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        conn.close()

def clean_message(message):
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
            if (is_valid_mail(mail)):
                already_exist.append(mail)
            else:
                query = "insert into mails (mail_id) values ('{0}');".format(mail)
                cursor.execute(query)
                conn.commit()
                added_mail.append(mail)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            app.logger.info(e)
            send_error_message(chatId)
            conn.close()
            return
    message = "No changes done\n"
    if (len(added_mail) > 0):
        message = "Inserted the following into the database\n"
        for mail in added_mail:
            message = message + "   ->" + mail + '\n'
    if (len(already_exist)):
        message = message + "The following already exist in the database\n"
        for mail in already_exist:
            message = message + "   ->" + mail
    send_message(chatId,message)
    return

def remove_mail(chatId,mails):
    mails = list(set(mails))
    conn,cursor = connect()
    not_present = []
    removed_mail = []
    for mail in mails:
        try:
            if (is_valid_mail(mail)):
                query = "delete from mail where mail_id = '{0}';".format(mail)
                cursor.execute(query)
                conn.commit()
                removed_mail.append(mail)
            else:
                not_present.append(mail)
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            app.logger.info(e)
            send_error_message(chatId)
            conn.close()
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
    send_message(chatId,message)
    return

def view_accepted_users(chatId):
    try:
        conn,cursor = connect()
        query = "select firstName,lastName from accepted_users"
        cursor.execute(query)
        names = cursor.fetchall()
        conn.close()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        app.logger.info(e)
        send_error_message(chatId)
        conn.close()
        return
    message = "Accepted Users are \n"
    for name in names:
        message = message + name[0] + " " +name[1] + '\n'
    send_message(chatId,message)

def draw_chart(chart_data,recieved_mails,expected_mails,pie):
    expectedy_axis_data = []
    y_axis_data = []
    x_axis_data = []
    x_axis_ticks = []
    x_axis_ticks_indices = []
    index = 0
    current_month = 0
    for tup in chart_data:
        date = tup[0]
        value = tup[1]
        expected_value = tup[2]
        if (index == 0 or index == len(chart_data) - 1):
            current_month = get_month_for_plot(date)
            x_axis_ticks.append(clean_date_for_plot(date))
            x_axis_ticks_indices.append(index)
        elif (get_month_for_plot(date) == current_month + 1):
            current_month = current_month + 1
            x_axis_ticks.append(clean_date_for_plot(date))
            x_axis_ticks_indices.append(index)
        x_axis_data.append(clean_date_for_plot(date))
        y_axis_data.append(value)
        expectedy_axis_data.append(expected_value)
        index = index + 1
    if (not pie):
        ax = plt.figure().gca()
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xticks(x_axis_ticks_indices,x_axis_ticks,rotation='horizontal')
        plt.tight_layout()
        plt.plot(x_axis_data,y_axis_data,label="actual")
        plt.plot(x_axis_data,expectedy_axis_data,linestyle='dashed', label="expected")
    else:
        sizes = [recieved_mails,expected_mails-recieved_mails]
        labels = 'Sent', 'Did Not Send'
        explode = (0,0.1)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes,explode=explode,labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
        ax1.axis('equal')

    stringtmp = "abcdefghijklmnopqrstuvwxyz"
    imgname = random.choice(stringtmp) + random.choice(stringtmp) + random.choice(stringtmp) + random.choice(stringtmp) + random.choice(stringtmp) + ".jpeg"
    f = open('images/'+imgname,'w+')
    f.close()
    app.logger.info(imgname)
    plt.savefig('images/'+imgname,format='jpeg')
    pic_url = "https://sandeshghanta.pythonanywhere.com/{0}/files/".format(values['bot_token']) + imgname
    return pic_url

def list_statistics(chatId,message):
    batches = values['batches']
    summary_message = "Statistics of "
    os.chdir('/home/sandeshghanta/mysite/')
    args = list(message.strip().split())

    try:
        if (args[0] == '-a'):
            summary_message = summary_message + "all users "
            args.insert(1,"allmail")
        elif (args[0] == '-i'):
            try:
                is_valid = is_valid_mail(args[1])
                if (not is_valid):
                    message = str(args[1]) + " is not a valid mail"
                    send_message(chatId,message)
                    return
            except IndexError:
                message = "Argument for -i not provided"
                send_message(chatId,message)
                return
            summary_message = summary_message + "of the individual "+args[1] + " "
        elif (args[0] == '-b'):
            try:
                if (args[1] not in batches):
                    message = str(args[1]) + " is not a valid batch. The available batches are " + ', '.join(batches)
                    send_message(chatId,message)
                    return
            except IndexError:
                message = "Argument for -b not provided"
                send_message(chatId,message)
                return
            summary_message = summary_message + "of the batch " + args[1] + " "
        else:
            errormsg = """Please check your arguments """ + args[0] + """ is not a valid option. The available options are -i, -g, -a
            -i stands for individual report. You can give an email as input
            -b stands for batch report. You can give a batch name as inputself.
            -a stands for overall report"""
            send_message(chatId,errormsg)
            return
    except IndexError:
        errormsg = "The first argument for /statistics method i.e -i,-a,-b is not provided"
        send_message(chatId,errormsg)
        return
    try:
        if (args[2] == '-h'):
            start_date = "01-07-18"
            args.insert(3,start_date)
            args.insert(4,get_today_date())
            summary_message = summary_message + "from " + start_date + " to " + str(get_today_date()) + ". "
        elif (args[2] == '-d'):
            if (len(args) == 3):
                args.insert(3,get_today_date())
                args.insert(4,get_today_date())
            else:
                is_valid,errormsg = is_valid_date(args[3])
                if (not is_valid):
                    user_provided_chart_flag = ' '.join(args[3:])
                    user_provided_chart_flag = user_provided_chart_flag.lower()
                    if not(user_provided_chart_flag == '-line' or user_provided_chart_flag == '-pie'):
                        errormsg = errormsg + ". Also {0} is not a chart flag. The availabe chart flags are -line and -pie".format(user_provided_chart_flag)
                        message = errormsg
                        send_message(chatId,message)
                        return
                    else:   #The user has provided a valid chart flag as the third argument. It means that the command is of the format -d -pie/-line
                        args.insert(3,get_today_date())
                else:
                    args[3] = errormsg  #If the date is valid then the is_valid_date method returns the modified date
                is_valid,errormsg = is_smaller_than_today(args[3])
                if (not is_valid):
                    message = errormsg
                    send_message(chatId,message)
                    return
                else:
                    args[3] = errormsg  #If the date is valid then the is_valid_date method returns the modified date
                args.insert(4,args[3])  #To maintain uniformity all the dates are in the -p format. If there is only one day 'x' then the program will search from x to x
            summary_message = summary_message + "on the day " + str(get_today_date()) + ". "
        elif (args[2] == '-p'):
            try:
                for i in range(3,5):    #i takes the values 3,4 args[i] denotes the dates
                    is_valid,errormsg = is_valid_date(args[i])
                    if (not is_valid):
                        message = errormsg
                        send_message(chatId,message)
                        return
                    else:
                        args[i] = errormsg  #if is_valid is true then errormsg is actually the formatted value of the date
                    is_valid,errormsg = is_smaller_than_today(args[i])
                    if (not is_valid):
                        message = errormsg
                        send_message(chatId,message)
                        return
                    else:
                        args[i] = errormsg
                summary_message = summary_message + "from " + str(args[3]) + " to " + str(args[4]) + ". "
            except IndexError:
                message = "-p flag requires two dates to be given. Two dates were not given"
                send_message(chatId,message)
                return
        else:
            errormsg = "The avaiable options for time are -d -p -a. " + args[2] + " is not a valid option " + """
            -d stands for a particular day. You can give a date input after this. The format is dd-mm-yy If no input is given after the -d flag today's date is taken by default
            -p stands for a period. You can give a two dates after the -p flag. Both the dates should be in dd-mm-yy format. The first date stands for the start date and the second date stands for end date. If the end date is not given the default value is the current date
            -h stands for history. The statistics returned will be from the start of time to the current date """
            send_message(chatId,errormsg)
            return
    except IndexError:
        errormsg = "The /statistics must require a time flag. The avaiable options are -d, -p, -h"
        send_message(chatId,errormsg)
        return
    #The Code below gets the statistics
    user_provided_chart_flag = ""
    if (len(args) > 5):
        user_provided_chart_flag = ''.join(args[5:])
        user_provided_chart_flag = user_provided_chart_flag.lower()
        if not(user_provided_chart_flag == '-line' or user_provided_chart_flag == '-pie'):
            errormsg = user_provided_chart_flag + " is not a valid chart flag. The valid options are -line and -pie"
            send_message(chatId,errormsg)
            return
    start_date = datetime.datetime.strptime(args[3],'%d-%m-%y')
    end_date = datetime.datetime.strptime(args[4],'%d-%m-%y')
    if (start_date > end_date):
        error_msg = "Start Date is greater than End Date. Please recheck your input!!"
        send_message(chatId,error_msg)
        return
    file = open('maildata.json','r')
    mail_json_data = json.load(file)
    file.close()
    count_of_students_in_batch = {}
    for batch in batches:
        count_of_students_in_batch[batch] = len(mail_json_data[batch])
    chart_data = []
    recieved_mails = 0
    expected_mails = 0
    while (start_date <= end_date):
        file_name = start_date.strftime('%d-%m-%y')
        try:
            with open('jsondata/'+file_name+'.txt') as fileobj:
                json_file_data = json.load(fileobj)
                if (args[0] == '-b'):
                    recieved_mails = recieved_mails + len(json_file_data[args[1]])
                    expected_mails = expected_mails + count_of_students_in_batch[args[1]]
                    chart_data.append((file_name,len(json_file_data[args[1]]),count_of_students_in_batch[args[1]]))
                elif (args[0] == '-i'):
                    sent = 0
                    for batch in json_file_data:
                        if (args[1] in json_file_data[batch]):
                            sent = 1
                            break
                    recieved_mails = recieved_mails + sent
                    expected_mails = expected_mails + 1
                    chart_data.append((file_name,sent,1))
                elif (args[0] == '-a'):
                    sent = 0
                    for batch in json_file_data:
                        sent = sent + len(json_file_data[batch])
                    total_no_of_students_in_batches = 0
                    for batch in count_of_students_in_batch:
                        total_no_of_students_in_batches = total_no_of_students_in_batches + count_of_students_in_batch[batch]
                    recieved_mails = recieved_mails + sent
                    expected_mails = expected_mails + total_no_of_students_in_batches
                    chart_data.append((file_name,sent,total_no_of_students_in_batches))
        except FileNotFoundError:
            #send_admin_message(file_name+'.txt' + " is not there in the server!!!")
            do_nothing = 1
        start_date = start_date + datetime.timedelta(days=1)
    summary_message = summary_message + str(recieved_mails) + " mails recieved," + str(expected_mails) + " were expected."

    #Below we are checking what type of chart the user asked for
    if (user_provided_chart_flag == ""):
        if (args[2] != '-d'):   #If -d flag is given the default option is pie and it cannot be changed
            pie = False
            if (args[0] == '-i'):
                pie = True
        else:
            pie = True
    else:
        if (user_provided_chart_flag == "-line"):
            pie = False
        else:
            pie = True
    pic_url = draw_chart(chart_data,recieved_mails,expected_mails,pie)

    summary_message = summary_message + " " + pic_url
    send_message(chatId,summary_message)

def list_admin_methods(chatId):
    message = " /grant_access *\n /view_accepted_users\n /send_message_to_all\n /add_mail\n /remove_mail\n /revoke_access\n /get_pending_requests\n"
    send_message(chatId,message)

def send_help(request_data):
    chat_id = str(request_data['message']['chat']['id'])
    message = request_data['message']['text'].strip()
    args = message.split(' ')
    file = open('help.json','r')
    help = json.load(file)
    file.close()
    if (len(args) == 1):
        send_message(chat_id,'\n'.join(help['welcome_message']),False,False)
        methods_help_message = ""
        for method in help['methods_help']:
            methods_help_message = methods_help_message + '\n'.join(help['methods_help'][method]) + '\n\n'
        send_message(chat_id,methods_help_message,False,False)
        send_message(chat_id,'\n'.join(help['warning_message']),False,False)
    else:
        args[1] = args[1].lower()
        message = "The method " + args[1] +" is not a valid method. Please check the list of availabe methods"
        if (args[1] in help['methods_help']):
            message = '\n'.join(help['methods_help'][args[1]])
        send_message(chat_id,message,False,False)

def handle_request(request_data):
    message = request_data['message']['text']
    chatId = str(request_data['message']['chat']['id'])
    message = clean_message(message)
    if ('username' not in request_data['message']['chat']):
        send_message(chatId,"You do not have a telegram username please do create one in settings and then use this bot!!!")
        return
    if (message.startswith('/start') or message.startswith('/help')):
        send_help(request_data)
    elif (message.startswith('/follow')):
        if (len(message) > 8):
            emails = list(message[8:].split(' '))
            follow(chatId,emails)
        else:
            message = "The /follow command requires some input to be given"
            send_message(chatId,message)
    elif (message.startswith('/unfollow')):
        if (len(message) > 10):
            emails = list(message[10:].split(' '))
            unfollow(chatId,emails)
        else:
            message = "The /unfollow command requires some input to be given"
            send_message(chatId,message)
    elif (message.startswith('/unfollow_all')):
        unfollow_all(chatId)
    elif (message.startswith('/list_following')):
        list_following(chatId)
    elif (message.startswith('/request_access')):
        request_access(request_data)
    elif (message.startswith('/list_all_mails')):
        list_all_mails(chatId)
    elif (message.startswith('/statistics')):
        if (len(message) == 11):
            send_message(chatId,"No input given for statistics")
        else:
            list_statistics(chatId,message[11:])
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
        elif (message.startswith('/view_accepted_users')):
            view_accepted_users(chatId)
        elif (message.startswith('/reset_webhook')):
            reset_webhook(chatId)
        elif (message.startswith('/list_admin_methods')):
            list_admin_methods(chatId)
        elif (message.startswith('/send_message_to_all')):
            if (len(message) > 13):
                message = message[13:]
                send_message_to_all(message)
            else:
                send_message(chatId,"Blank Message Provided")
        else:
            message = "Invalid input"
            send_message(chatId,message)
    else:
        message = "Invalid Input"
        send_message(chatId,message)

values = {}     #Defining an dictionary containing all the confidential data in global scope to make sure all functions get access to it
with open("values.json","r") as file:
    values = json.load(file)

@app.route("/"+values['bot_token'], methods=['GET','POST'])
def webhook():
    request_data = request.get_json()
    chatId = ""
    if ('message' in request_data):
        try:
            chatId = str(request_data['message']['chat']['id'])
        except KeyError:
            try:
                chatId = str(request_data['message']['from']['id'])
            except KeyError:
                send_admin_message(str(request_data))
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    else:
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}    #As of now edited messages are not supported
    if (not exists_in_db(chatId)):
        add_entry_to_user_in_db(request_data)
    handle_request(request_data)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route("/"+values['bot_token']+'/files/<path:path>')
def get_file(path):
    """Download a file."""
    UPLOAD_DIRECTORY = 'images'
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

if __name__ == '__main__':
    os.chdir('/home/sandeshghanta/mysite/')
    app.run(host='0.0.0.0',port="1234")
