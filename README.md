# Status Update Bot

A telegram bot which gets the status updates of the amfoss members and sends them to you personally via chat.

## Getting Started

1. Clone the repository
2. Install Python 3.7 in your system. [link](https://www.python.org/downloads/)
3. Install the python modules required the script to work.
* requests [link](http://docs.python-requests.org/en/v2.7.0/user/install/)

* matplotlib.pyplot [link](https://matplotlib.org/users/installing.html)

* MySQLdb [link](https://geeksww.com/tutorials/web_development/python/installation/how_to_download_and_install_mysqldb_module_for_python_on_linux.php)

* flask [link](http://flask.pocoo.org/docs/1.0/installation/#install-flask)

* googleapiclient [link](https://developers.google.com/gmail/api/quickstart/python)

There are several other modules which this script uses like json, base64, os etc.. these modules are already installed so there is no need to do any kind of special installation

## Running the tests

Will add them soon

### Break down into end to end tests

Will add them soon
```
Give an example
```

## Deployment

To deploy this script online one must have access to a free hosting platform like pythonanywhere and also must be a member in a google groups where emails are sent regularly. The title of the email should satisfy the given requirements i.e "[FOSS-2017] Status Update-13/10/18". Since being a member of a google group where such kinds of mails are regularly sent is difficult, it is recommended to change the name of the mail to be searched by modifying the code in [this](https://github.com/sandeshghanta/Status_Update_Bot/blob/887457a7f61b1bbebbda7941006e2b56ae75f8dd/gmail_api.py#L112) file
Anyone who wants to contribute can test their changes by 
1. To test the bot you must create your own bot in [telegram] (https://core.telegram.org/bots)
2. To host the code you can use any free hosting server pythonanywhere is recommended
3. You must set up a webhook liking the bot to the webserver [link] (https://medium.com/@xabaras/setting-your-telegram-bot-webhook-the-easy-way-c7577b2d6f72)
4. While hosting the code in the webserver make sure you change the values in the values.json [file](https://github.com/sandeshghanta/Status_Update_Bot/blob/master/values.json). You must give the details of your telegram bot.
5. Also make sure you add the gmail api keys required by the gmail_api.py file to the server. To do this just generate your keys just follow [this] (https://developers.google.com/gmail/api/quickstart/python). At the end of the process you will be getting two files credentials.json and token.json. Just upload those files to the server too.
6. Use this [link] (https://medium.com/@rudder_/launching-a-flask-app-from-scratch-on-pythonanywhere-fef871171e18) for reference while uploading to pythonanywhere
7. The gmail_api.py script sends the daily notifications to users. This script is run everyday at 23:45 UTC via a cron job. In your server you can change the time according to your choice. Use this [link] (https://help.pythonanywhere.com/pages/ScheduledTasks/) to know how to set up a cron job in pythonanywhere
8. The following tables exist in the database
    ![accepted_users](https://preview.ibb.co/fgsN70/accepted-users.png)
    ![admin](https://preview.ibb.co/h7hN70/admin.png)
    ![mails](https://preview.ibb.co/ndKfuf/mails.png)
    ![pending-requests](https://preview.ibb.co/mPQLuf/pending-requests.png)
    ![user](https://preview.ibb.co/mXDOEf/user.png)

## Screenshots

Will add them soon

## Built With

* [python](http://www.dropwizard.io/1.0.2/docs/) - Language used
* [Bot API](https://core.telegram.org/bots/api) - Bot API
* [Gmail API](https://developers.google.com/gmail/api/) - Gmail API

## Authors

* **Sandesh Ghanta** - *Initial work* - [sandeshghanta](https://github.com/sandeshghanta)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* I would like to thank pythonanywhere for providing a free hosting platform and google, telegram for providing such wonderful api's
