# compcode
A python script to add all upcoming contest from CodeChef, HackerRank and CodeForces to your google calendar

We just need to execute the exec.py for once.
What the script does
1. Ask for authentication when you run the script for the first time.
2. Will go to stopstalk and add upcoming contest of CodeChef, HackerRank and CodeForces to your Primary Google Calendar.
3. Will set a cronjob that'll run this script every 12 hours and add new contests found.

You need to edit the script first.

In the exec.py script change the username to your user account's name
'''
cron = CronTab(user='username')
'''
Also change the address from 'python3 ./compcode.py' to the full directory path like below
'''
python3 /home/tmw98/Codes/python/scritps/compcode.py
'''

In the compcode.py script change the username and password to your MySQL's username and password
'''
db_cursor, db= connect_db('username', 'password')
'''
a
Now to get access to your Google Calendar you need to go through this page and do the quick start method
It'll give you a client.json file rename it to client_secret.json and paste it in the folder with scripts.

And do place all the scritps in one single folder before running them.

You just need to run the exec.py once, It'll automatically add a cronjob to run that script every 12 hours
