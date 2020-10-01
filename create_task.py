# import os
import subprocess
import datetime
import argparse
import shift_manager

aparse = argparse.ArgumentParser(description='Run the CWP.')
aparse.add_argument('-devops', action='store_true', help='9:30 dev ops meeting')
aparse.add_argument('-sossa', action='store_true', help='sossa')
aparse.add_argument('-minutes_meeting', action='store_true', help='send Mattius info')
args = aparse.parse_args()


class CreateTask:

    def __init__(self):
        self.user = 'andrew'
        self.SM = shift_manager.ShiftManager()
        self.task_start = ['task', 'add']
        self.tag = ['+shift']
        self.now = datetime.datetime.now()
        self.today = datetime.datetime.strftime(self.now, '%Y-%m-%d')

    def eos(self):
        shift = self.on_shift_at(self.now)
        time = shift['shift_end'][:-1]
        time = time + ':00'
        return time

    def send_cmd(self, cmd):
        out = subprocess.Popen(cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        normalout = stdout.decode('utf-8').split('\n')
        try:
            normalerr = stderr.decode('utf-8').split('\n')
        except AttributeError:
            normalerr = ''
        return normalout, normalerr

    def on_shift_at(self, time):
        shift_details = self.SM.shift_check(time)
        return shift_details

    def user_on_now(self):
        # self.shift_details = self.on_shift_at(datetime.datetime.now())
        self.shift_details = self.on_shift_at(self.now)
        if self.shift_details['worker'].upper() == self.user.upper():
            return True
        else:
            return False

    def devops_meeting(self):
        "every morning at 7am only if im on days"
        if self.user_on_now():
            message = 'Run the 9:30 DevOps meeting'
            trigger = self.now.replace(hour=9, minute=30, second=0, microsecond=0)
            due = datetime.datetime.strftime(trigger, '%H:%M:%S')
            task = self.task_start + message.split(' ') + self.tag + [f'due:{due}']
            # print(self.task_start + task + self.tag + ' due:' + due)
            # print(task)
            # print(' '.join(task))
            norout, norerr = self.send_cmd(task)
            print(norout)
            print(norerr)

    def sossa(self):
        "every morning at 2pm only if im on swings"
        if self.user_on_now():
            message = 'Check SOSSA rejections'
            trigger = self.now.replace(hour=15, minute=0, second=0, microsecond=0)
            due = datetime.datetime.strftime(trigger, '%H:%M:%S')
            task = self.task_start + message.split(' ') + self.tag + [f'due:{due}']
            norout, norerr = self.send_cmd(task)
            print(norout)
            print(norerr)


    def minutes_meeting(self):
        "every Monday at 2am only if im on mids"
        if self.user_on_now():
            message = 'Minutes meeting with Mattius'
            due = self.eos()
            task = self.task_start + message.split(' ') + self.tag + [f'due:{due}']
            norout, norerr = self.send_cmd(task)
            print(norout)
            print(norerr)





    

CT = CreateTask()
# if CT.user_on_now():
#     print('create task')

if args.devops:
    CT.devops_meeting()

if args.sossa:
    CT.sossa()

if args.minutes_meeting:
    CT.minutes_meeting()
