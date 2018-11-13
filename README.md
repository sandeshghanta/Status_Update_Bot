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

# Project Title

A telegram bot which gets the status updates of the amfoss members and sends them to you personally via chat.

## Getting Started

1. Clone the repository
2. Install Python 3.7 in your system. [link](https://www.python.org/downloads/)
3. Install the python modules required the script to work.
*requests [link](http://docs.python-requests.org/en/v2.7.0/user/install/)
*matplotlib.pyplot [link](https://matplotlib.org/users/installing.html)
*MySQLdb [link](https://geeksww.com/tutorials/web_development/python/installation/how_to_download_and_install_mysqldb_module_for_python_on_linux.php)
*flask [link](http://flask.pocoo.org/docs/1.0/installation/#install-flask)
*googleapiclient [link](https://developers.google.com/gmail/api/quickstart/python)

There are several other modules which this script uses like json, base64, os etc.. these modules are already installed so there is no need to do any kind of special installation

## Running the tests

Will add them soon

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Anyone who wants to contribute must have
1. Telegram account [telegram](https://play.google.com/store/apps/details?id=org.telegram.messenger&hl=en_IN)
2. pythonanywhere account [pythonanywhere](https://www.pythonanywhere.com/)

## Screenshots

Will add them soon

## Built With

* [python](http://www.dropwizard.io/1.0.2/docs/) - Language used
* [Bot API](https://core.telegram.org/bots/api) - Bot API
* [Gmail API](https://developers.google.com/gmail/api/) - Gmail API

## Contributing
Will update this soon

## Authors

* **Sandesh Ghanta** - *Initial work* - [sandeshghanta](https://github.com/sandeshghanta)

[comment]: <> See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* I would like to thank pythonanywhere for providing a free hosting platform and google, telegram for providing such wonderful api's
