'''
    Gets details of upcoming contests from CodeChef, HackerRank, and CodeForces from stopstalk and adds them to your Google Calendar
'''

import googleauth
import MySQLdb as db
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

# Script to connect to local database
def connect_db(username, password):
    temp_db = db.connect("localhost", username, password)
    temp_cursor = temp_db.cursor()
    return temp_cursor, temp_db

# Initialize BeautifulSoup Object
def init_bs_obj():
    page = requests.get('https://www.stopstalk.com/contests')
    source_code = page.text
    return BeautifulSoup(source_code, "html.parser")

'''
    takes start_time and run_time as input
    and returns start_time and end_time if a particular string format
    to be added to the calendar
'''
def get_time(start_time, run_time_hrs, run_time_mins):
    start_time = datetime(int(start_time[:4]), int(start_time[5:7]), int(start_time[8:10]), int(start_time[11:13]), int(start_time[14:16]), int(start_time[17:]))
    end_time = start_time + timedelta(hours = int(run_time_hrs), minutes = int(run_time_mins))
    start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    return start_time, end_time

'''
    Separates runtime in runtime hours and mintues
'''
def set_runtime(run_time):
    run_time_mins = 0
    run_time_hrs = 0
    if len(run_time.split()) > 1:
        run_time_hrs = run_time.split()[0][:-1]
        run_time_mins = run_time.split()[1][:-1]
    else:
        if run_time[-1] == 'h':
            run_time_hrs = run_time[:-1]
        else:
            run_time_mins = run_time[:-1]
    return run_time_hrs, run_time_mins

'''
    Find the upcoming contests of passed websites
    and put them in a list to be added to database and Google Calendar
'''
def find_contests(soup_obj, web):
    if web == 'CodeChef':
        imgs = soup_obj.findAll('img', {'title' : 'CodeChef'})
    elif web == 'HackerRank':
        imgs = soup_obj.findAll('img', {'title' : 'HackerRank'})
    elif web == 'Codeforces':
        imgs = soup_obj.findAll('img', {'title' : 'Codeforces'})
    else:
        pritn("ERROR NO WEBSITE EXITSTS")
        exit(1)

    contest_list = []

    # For this part you have to read the source code of https://www.stopstalk.com/contests thoroughly

    for img in imgs:
        butt = img.findNext('button')
        if 'Already started!' in butt.get('data-tooltip') or 'Div. 1' in img.findParent().findPrevious().text:
            continue
        contest_name = str(img.findParent().findPrevious().text)
        run_time = str(img.findNext('td').findNext('td').text)
        run_time_hrs, run_time_mins = set_runtime(run_time)
        start_time = str(img.findNext('td').text)
        # print(start_time)
        start_time, end_time = get_time(start_time, run_time_hrs, run_time_mins)
        link = img.findNext('a').get('href')

        # this format needs to be maintained to add in Google Calendar
        event = {
            'summary' : contest_name,
            'location' : link,
            'description' : contest_name,
            'start' : {
                'dateTime' : start_time,
                'timeZone' : 'Asia/Kolkata',
            },
            'end' : {
                'dateTime' : end_time,
                'timeZone' : 'Asia/Kolkata',
            },
            'reminders' : {
                'userDefault' : True,
            },
        }
        contest_list.append(event)
    return contest_list

# adds events in the list in Primary Google Calnedar specified to the email address
def add_to_calendar(calendar_credentials, contest_list):
    for event in contest_list:
        calendar_credentials.events().insert(calendarId = 'primary', body = event).execute()

'''
    Checks if contest is already added i.e present in database then don't append in the new list
    to be added to the Google Calendar, if not present then append it to be added
'''
def add_to_database(db_cursor, contest_list):
    new_list = []
    for contest in contest_list:
        contest_name = contest['summary'].replace("'", "").replace('"', '')
        start_time = contest['start']['dateTime'][:10] + " " + contest['start']['dateTime'][11:19]
        end_time = contest['end']['dateTime'][:10] + " " + contest['end']['dateTime'][11:19]
        query = db_cursor.execute(r"SELECT CONTEST_NAME FROM contests WHERE CONTEST_NAME = '{}' AND START_TIME = '{}'".format(contest_name, start_time))
        if query != 0:
            continue
        new_list.append(contest)
        db_cursor.execute('''
            INSERT INTO contests (CONTEST_NAME, START_TIME, END_TIME)
            VALUES ("{}", "{}", "{}")
        '''.format(contest_name, start_time, end_time))
    return new_list


# Just the function calling part Here
def main():
    calendar_credentials = googleauth.googlekiscript()

    # Add your username and password for MySQL databse
    db_cursor, db= connect_db('username', 'password')

    db_cursor.execute('CREATE DATABASE IF NOT EXISTS compcode;')
    db_cursor.execute('USE compcode;')
    sql_query = '''
        CREATE TABLE IF NOT EXISTS contests (
        ID int PRIMARY KEY AUTO_INCREMENT,
        CONTEST_NAME varchar(255),
        START_TIME DATETIME,
        END_TIME DATETIME
        )
        '''
    db_cursor.execute(sql_query)
    soup_obj = init_bs_obj()
    codechef_dict = find_contests(soup_obj, 'CodeChef')
    codechef_dict = add_to_database(db_cursor, codechef_dict)
    add_to_calendar(calendar_credentials, codechef_dict)
    hackerrank_dict = find_contests(soup_obj, 'HackerRank')
    add_to_database(db_cursor, hackerrank_dict)
    add_to_calendar(calendar_credentials, hackerrank_dict)
    codeforces_dict = find_contests(soup_obj, 'Codeforces')
    add_to_database(db_cursor, codeforces_dict)
    add_to_calendar(calendar_credentials, codeforces_dict)
    db.commit()

if __name__ == '__main__':
    main()
