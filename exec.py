import compcode
from crontab import CronTab
import subprocess

'''
    Lol just for cronjob made this new file
'''
def main():

    #Change username
    cron = CronTab(user='username')

    for job in cron:
        if 'python3 ./compcode.py' in str(job):
            exit(1)
    subprocess.call(['python3', './compcode.py'])
    job = cron.new(command='python3 ./compcode.py')
    job.hour.every(12)
    cron.write()


if __name__ == '__main__':
    main()
