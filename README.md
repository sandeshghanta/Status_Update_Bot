# Status_Update_Bot
A telegram bot for getting status updates.

Hello, Welcome to the Status Update Bot!
It is great to see you here.
Everyday you wish to see the status updates of some people, let it be your mentee/mentor. But searching for that particular mail is difficult in the thread\n
This bot helps you with that. All you have to do is to 'follow' whosever updates you want to get. This bot will send you their status updates to via Telegram chat!\n
The methods which are accessable to you are
1) /follow: Using this command you can follow others. You can give multiple email id's at once.(space seperated)
    Ex: /follow mail1
    Ex: /follow mail1 mail2

2) /unfollow: Using this command, you can unfollow a person who you already follow. You can give multiple email id's at once. (space seperated).
    Ex: /unfollow mail1
    Ex: /unfollow mail1 mail2

3) /unfollow_all: Using this command, you can unfollow all the people who you currently follow. This command requires no arguments.
    Ex: /unfollow_all

4) /list_following: Lists all the people who you are currently following. This command takes no arguments.
    Ex: /list_following

5) /list_all_mails: Lists all the mails in the FOSS'17 group. This command takes no arguments.
    Ex: /list_all_mails

6) /request_access: Requests the admin to grant you access to recieve mail. This command takes no arguments
    Ex: /request_access

7) /help: Displays this message
    Ex: /help
    
8) /statistics: There are three arguements to this command. The first two arguments are MANDATORY for the query to execute
        The first argument is to know whom to check for. The available options are -i, -b, -a.
            • -i stands for individual user. After the -i flag you can give the email address of the person you want.
                Ex: /statistics -i mail1
            • -b stands for batch. After the -b flag you can mention the batch you want to track. The available options as of now are 2015,2016 and 2017
                Ex: /statistics -b 2016
            • -a stands for all users. All the people in the FOSS mailing list will be considered.
                Ex: /statistics -a
        The second argument is for time period. The available options are -d, -p, -h
            • -d stands for a day. After the -d flag you can give a day in dd-mm-yy format. If no argument is given then by default yesterdays day is taken
                Ex: /statistics [argument1] -d 02-07-18
                    /statistics [argument1] -d
                Examples of acceptable dates
                    2-7-18
                    02-7-18
                    2-07-18
                    02-07-18
            • -p stands for period. You must specify two dates after this flag. The first date is the start_date and the second date is the end_date. The dates should be of dd/mm/yy format.
                Ex: /statistics [argument1] -p 02-07-18 02-08-18
            • -h stands for history. It means that you will get the analysis from the start of time (in our case 01-07-18) to yesterdays date. No input is needed after this flag
                Ex: /statistics [argument1] -h
        The third argument is for knowing the type of graph to display output. The availabe options are -pie, -line. This argument is OPTIONAL
            For the -i flags the default value is -pie
            For the -a, -h flags the default value is -line
            But you override these default values by simply mentioning the flag you want
            NOTE: If the -d flag is used the default value is -pie and it cannot be overriden because there is no point in viewing a line graph with one node :P
            Ex: /statistics [argument1] [argument2] -pie
                /statistics [argument1] [argument2] -line

        Ex: /statistics -i mail1 -d
            /statistics -b 2016 -p 02/07/18 15/7/18
            /statistics -b 2016 -h
            /statistics -a -h
            (and many more combinations supported)",

*NOTE*: This is a public bot. To make sure that the wrong people do not get the status updates of the FOSS mailing list you are required to request access from the admin. All you have to do is send the /request_access command. Until the admin accepts your request, you will not be getting the status updates of others. But you can keep editing your preferences till then i.e you can add who to follow and not. Once the admin accepts your request, you will be getting a notification. Similary the admin can revoke your access at any point of time.
You will be receiving the status updates of the previous day daily at 5:10 AM
Please check if your mail is present in /list_all_mails
If not, please do ping me at sghanta05@gmail.com or 8137069878.
