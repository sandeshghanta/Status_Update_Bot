import MySQLdb
file = open('nofile.txt','r')
mails = []
for line in file:
    mails.append(line)
conn=MySQLdb.connect(host='stop-looking',user='at-personal',passwd='stuff-you-creep')
cursor = conn.cursor()
cursor.execute('use sandeshghanta$userdata')
for mail in mails:
    query = "insert into mails(mail_id) values ('" + mail.strip() + "');"
    cursor.execute(query)
conn.commit()
conn.close()
