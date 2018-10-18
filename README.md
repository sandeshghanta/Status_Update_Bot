# Status Update Bot

Get your friends status updates instantly to your chat via this telegram bot.

## Getting Started
These bot will help you to get the instant updates as well as search for the thread messages at ease. Following are the list of slash commands that is configured in this status update bot

1. /follow: This command helps you to follow others. (__viz.__ /follow mailid1 or /follow mailid1 mailid2)
2. /unfollow: This command helps you to unfollow. (__viz.__ /unfollow mailid1 or /unfollow mailid1 mailid2)
3. /unfollow_all: This command will helps you to unfollow all the people who you currently follow. 
4. /list_following: Get the list of people's names you are following.
5. /list_all_mails: Get the list of people's email id's you are following.
6. /request_access: This command will request admin to grant their permission for receiving mail.
7. /statistics: Get the statistics or indepth details of each mail id. There are three arguments that is needed:
    -i : stands for individual user
    -b : stands for batch
    -a : stands for all users
    -d : stands for day (format is dd-mm-yy). If none is given it takes yesterday's date by default.
    -p : stands for time period. The first argument contains start date and second with end date. (format is dd-mm-yy)\
    -h : stands for history.  
    ```
    /statistics -i mailid1
    /statistics -b 2016
    /statistics -b 2016 -h
    /statistics -b 2016 -p 02-07-18 15-07-18
    ```
8. /help: This command will display list of slash commands with description.

## Authors

* **Sandesh Ghanta** - [Github](https://github.com/sandeshghanta)
