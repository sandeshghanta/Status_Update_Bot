import datetime

def clean_arg_for_date(x):
    x = str(x)
    if (len(x) == 1):
        x = '0' + x
    return x[-2:]   #Returns the last two characters used for years. i.e 2018 will be returned as 18

def clean_date_for_plot(x):
    x = str(x)
    args = list(x.split('-'))
    args = args[:-1]
    index = 0
    for arg in args:
        while (len(arg) > 0 and arg[0] == '0'):
            arg = arg[1:]
        args[index] = arg
        index = index + 1
    return '/'.join(args)

def get_month_for_plot(x):
    x = str(x)
    args = list(x.split('-'))
    while (len(args[1]) > 0 and args[1][0] == '0'):
        args[1] = args[1][1:]
    return int(args[1])

def get_today_date():
    now = datetime.datetime.now()  #To go to the previous day
    day = clean_arg_for_date(now.day)
    month = clean_arg_for_date(now.month)
    year = clean_arg_for_date(now.year)
    return day+'-'+month+'-'+year

def is_valid_date(date):
    days_in_month = [-1,31,28,31,30,31,30,31,31,30,31,30,31]    #Not supposed to change in the near future!!
    date = str(date)
    if ('/' in date):
        errormsg = "Date should be in dd-mm-yy format. NOT dd/mm/yy format. Please correct it"
        return (False,errormsg)
    for i in date:      #Checking if all characters are digits or not
        if ((ord(i) >= 48 and ord(i) <= 57) or ord(i) == 45):
            continue
        else:
            errormsg = data + " is not a valid date. " + i + " is an invalid character"
            return (False,errormsg)

    args = list(date.split('-'))
    args = list(filter(("").__ne__, args))
    args = list(filter((" ").__ne__, args))
    if (len(args) != 3):    #If there are any more or less than 3 args then it means the date is wrong
        errormsg = "A date must have exactly 3 arguments " + date + " does not have 3 arguments"
        return (False,errormsg)
    for i in range(0,3):
        if (len(args[i]) > 2):
            errormsg = date + " is not a valid date. "+ args[i] + " is not valid"
            return (False,errormsg)
        args[i] = clean_arg_for_date(args[i])  #Adding a '0' at the front if len is 1 to maintain uniformity

    if (int(args[1]) <= 0 or int(args[1]) > 12):    #Month must lie in between 1 and 12
        errormsg = args[1] + " is not a valid month"
        return (False,errormsg)

    if (int(args[0]) > days_in_month[int(args[1])] or int(args[0]) <= 0):    #Checking if those many days are there in the month
        errormsg = args[0] + " days do not exist in the month " + args[1]
        return (False,errormsg)
    if (int(args[1]) < 7 or int(args[2]) < 18):
        errormsg = "Our analysis starts from 01/07/18. " + date + " is older than that!!"
        return (False,errormsg)
    return (True,'-'.join(args))

def is_smaller_than_today(date):    #Method returns True if the date is smaller than today
    args = list(date.split('-'))
    args = list(filter(("").__ne__, args))
    args = list(filter((" ").__ne__, args))
    try:
        input_date = datetime.datetime.strptime('-'.join(args),'%d-%m-%y')
        today = datetime.datetime.now()
        if (today <= input_date):
            errormsg = "The date " + '-'.join(args) + " is either equal to greater than today. That is not allowed"
            return (False,errormsg)
    except:
        errormsg = "Error while parsing date " + '-'.join(args)
        return (False,errormsg)
    return (True,'-'.join(args))

def get_days_in_words():
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    now = datetime.datetime.now()
    today = now.strftime("%a")
    today_index = days.index(today)
    yesterday_index = (today_index - 1)%7
    yesterday = days[yesterday_index]
    tomorrow_index = (today_index + 1)%7
    tomorrow = days[tomorrow_index]     #This is added because I am not sure if server time is UTC or IST.
    return [today,yesterday,tomorrow]
