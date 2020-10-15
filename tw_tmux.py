import argparse
import logging
import libtmux
import os

# https://libtmux.git-pull.com/api.html

working_directory = os.environ['HOME'] + f'/shift_manager/'

# Logging
logit = logging.getLogger('TaskWarrior')
logit.setLevel(logging.DEBUG)
log_file = working_directory + 'logs/tmux_logging.log'
fh = logging.FileHandler(log_file)
ch = logging.StreamHandler()
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.WARN)

# Argparse
aparse = argparse.ArgumentParser(description='Task Warrior TMUX wrapper')
aparse.add_argument('--attatch', action='store_false', help='Dont attatch the process')
aparse.add_argument('--exit', action='store_false', help='Dont kill the process at exit')
aparse.add_argument('-p', action='append', help='Project flag')
aparse.add_argument('-t', action='append', help='Tag flag')
aparse.add_argument('-pri', action='append', help='Priority above/below')
aparse.add_argument('-set', action='append', help='Pre set displays')
aparse.add_argument('-kill', action='store_false', help='Find and close session with matching name')
aparse.add_argument('--killall', action='store_true', help='Find and close ALL sessions with matching name')

args = aparse.parse_args()
print(args)

logit.info(f"args:{args}")

def _update_name(session_name, count = 0):
    session_name = list(session_name)
    while True:
        try:
            int(session_name[-1])
        except ValueError:
            session_name.append(str(count))
            return ''.join(session_name), count
        else:
            session_name.pop(-1)
            count += 1

# def create_grid(window, x=1, y=1):
#     """Create the rows"""
#     for j in range(y-1):
#         window.cmd('split-window', '-v')
#     """Create the columns"""
#     for j in range(y):
#         pane_number = j * x
#         window.cmd('select-pane', '-t', str(pane_number))
#         for i in range(x-1):
#             window.cmd('split-window', '-h')
#     """Itterate through and resize"""
#     rows, columns = os.popen('stty size', 'r').read().split()
#     pane_x = int(columns)
#     pane_y = int(rows)
#     for p in range(x * y):
#         # If we are on the right or bottom edge we dont want to re-size the dimentions of the pane
#         if (p+1) % x == 0:
#             right_side = False
#         else:
#             right_side = True
#         if p >= x*y-x:
#             bottom_side = False
#         else:
#             bottom_side = True

#         window.cmd('select-pane', '-t', str(p))
#         if right_side:
#             window.cmd('resize-pane', '-x', str(pane_x // x))
#         if bottom_side:
#             window.cmd('resize-pane', '-y', str(pane_y // y))
#         # window.cmd('send-keys', f'echo {p}', 'C-m')

class Command:

    def __init__(self):
        self.projects = []
        self.tags = []
        self.priorities = []
        self.status = []
        self.cmd = ''
        self.empty = True

    """project"""
    def andproject(self, project):
        self.empty = False
        if self.projects == []:
            self.projects.append(f"project:{project}")
        else:
            self.projects.append(f"and project:{project}")

    def orproject(self, project):
        self.empty = False
        if self.projects == []:
            self.projects.append(f"project:{project}")
        else:
            self.projects.append(f"or project:{project}")

    def noproject(self, project):
        self.empty = False
        self.projects = ['project:']
        # self.projects.append(f"project:")


    """tag"""
    def andtag(self, tag):
        self.empty = False
        if self.tags == []:
            self.tags.append(f"+{tag}")
        else:
            self.tags.append(f"+{tag}")

    def ortag(self, tag):
        self.empty = False
        if self.tags == []:
            self.tags.append(f"+{tag}")
        else:
            self.tags.append(f"or +{tag}")

    def nottag(self, tag):
        self.empty = False
        if self.tags == []:
            self.tags.append(f"-{tag}")
        else:
            self.tags.append(f"-{tag}")

    def notag(self, tag):
        self.empty = False
        self.tags = ['tag:']
        # if self.tags == []:
        #     self.tags.append(f"tag:")
        # else:
        #     self.tags.append(f"tag:")


    """priority"""
    def andpriority(self, priority):
        self.empty = False
        priority = priority.upper()
        if priority not in ['H', 'M']:
            raise ValueError('Not a valid priority')
        if self.priorities == []:
            self.priorities.append(f"priority:{priority}")
        else:
            self.priorities.append(f"and priority:{priority}")

    def orpriority(self, priority):
        self.empty = False
        priority = priority.upper()
        if priority not in ['H', 'M']:
            raise ValueError('Not a valid priority')
        if self.priorities == []:
            self.priorities.append(f"priority:{priority}")
        else:
            self.priorities.append(f"or priority:{priority}")

    def nopriority(self, priority):
        self.empty = False
        self.priorities = ['priority:']
        # if self.priorities == []:
        #     self.priorities.append(f"priority:")
        # else:
        #     self.priorities.append(f"priority:")


    """status"""
    def andstatus(self, status):
        self.empty = False
        if status not in ['pending', 'complete', 'deleted']:
            raise ValueError('Not a valid priority')
        if self.status == []:
            self.status.append(f"status:{status}")
        else:
            self.status.append(f"and status:{status}")

    def orstatus(self, status):
        self.empty = False
        if status not in ['pending', 'complete', 'deleted']:
            raise ValueError('Not a valid priority')
        if self.status == []:
            self.status.append(f"projestatusct:{status}")
        else:
            self.status.append(f"or prostatusject:{status}")

    def nostatus(self, status):
        self.empty = False
        self.status = ["status:"]
        # if self.status == []:
        #     self.status.append(f"status:")
        # else:
        #     self.status.append(f"or status:{project}")


    # def mark_empty(self):
    #     self.empty = True

    def set_cmd(self):
        cmd_lst = [
            f'sh {working_directory}sim_watch.sh "', 
            'task',
        ] + \
        self.projects + \
        self.tags + \
        self.priorities + \
        self.status + \
        ['"']
        if self.empty:
            self.cmd = ''
            return self.cmd
        else:
            new_cmd = ' '.join(cmd_lst)
            self.cmd = ''.join(new_cmd)
            self.cmd
        # elif len(cmd_lst) == 0:
        #     # self.cmd = '"task"'
        #     new_cmd = ' '.join(cmd_lst[0,1])
        #     self.cmd = ''.join(new_cmd)
        #     return self.cmd
        # elif len(cmd_lst) == 1:
        #     new_cmd = '"task ' + cmd_lst[0] + '"'
        #     self.cmd = ''.join(new_cmd)
        #     return self.cmd
        # else:
        #     new_cmd = ' '.join(cmd_lst)
        #     # new_cmd = '"task ' + ' and '.join(cmd_lst) + '"'
        #     self.cmd = ''.join(new_cmd)
        #     return self.cmd
        return self.cmd


class TaskWarriorTmux:

    def __init__(self, session_name):
        self.orig_session_name = session_name
        self.session_name = self.orig_session_name
        self.cmd_lst = [[Command()]]
        # self.cmd_lst[0][0].append(self.Command())
        self.cmd = [0, 0]

        self.server = libtmux.Server()
        self.create_session()
        # self.create_window()
        self.select_window(0).select_pane(0)

        # print(self.cmd)
        # print(self.cmd_lst)
        # self.create_window()
        # self.select_window(1)
        # print(self.cmd)
        # print(self.cmd_lst)
        # print(self.cmd_lst[self.cmd[0]])
        # print(self.cmd_lst[self.cmd[0]][self.cmd[1]])
        # self.split_window()
        # print(self.cmd)
        # print(self.cmd_lst)
        # print(self.window)
        # print(self.pane)

        # print(self.cmd_lst[self.cmd[0]])


    def create_session(self, session_name=None):
        if session_name == None:
            session_name = self.session_name
        count = 0
        while True:
            try:
                session = self.server.new_session(session_name)
                break
            except libtmux.exc.TmuxSessionExists:
                session_name, count = _update_name(session_name, count)
        self.session = session
        self.session_name = session_name
        return self.session

    def create_window(self, new_window_name=''):
        self.window = self.session.new_window()
        self.cmd_lst.append([Command()])
        return self.window

    def split_window(self, vert_bool=True):
        self.pane = self.window.split_window(vertical=vert_bool,attach=True)
        self.cmd_lst[self.cmd[0]].append([Command()])
        return self.pane

    def add_cmd(self):
        self.cmd_lst[self.cmd[0]].append(Command())

    def select_window(self, number):
        self.window = self.session.select_window(number)
        self.cmd[0] = number
        return self.window

    def select_pane(self, number):
        self.pane = self.window.select_pane(number)
        self.cmd[1] = number
        return self.pane

    def create_grid(self, x=1, y=1):
        """Create the rows"""
        for j in range(y-1):
            self.window.cmd('split-window', '-v')
            self.add_cmd()
        """Create the columns"""
        for j in range(y):
            pane_number = j * x
            self.window.cmd('select-pane', '-t', str(pane_number))
            for i in range(x-1):
                self.window.cmd('split-window', '-h')
                self.add_cmd()
        """Itterate through and resize"""
        rows, columns = os.popen('stty size', 'r').read().split()
        pane_x = int(columns)
        pane_y = int(rows)
        for p in range(x * y):
            # If we are on the right or bottom edge we dont want to re-size the dimentions of the pane
            if (p+1) % x == 0:
                right_side = False
            else:
                right_side = True
            if p >= x*y-x:
                bottom_side = False
            else:
                bottom_side = True

            self.window.cmd('select-pane', '-t', str(p))
            if right_side:
                self.window.cmd('resize-pane', '-x', str(pane_x // x))
            if bottom_side:
                self.window.cmd('resize-pane', '-y', str(pane_y // y))

    def resize_pane(self, pane, horz, vert):
        self.select_pane(pane)
        if vert > 0: 
            self.pane.resize_pane(height=vert)
        if horz > 0:
            self.pane.resize_pane(width=horz)
        # self.pane.resize_pane(height=vert, width=horz)

    def close_pane(self, pane):
        self.select_pane(pane)
        self.cmd_lst[self.cmd[0]].pop(pane)
        self.pane.cmd('kill-pane')
        # self.pane.send_keys(f'exit', enter=True)

    def set_cmds(self):
        for el in self.cmd_lst[self.cmd[0]]:
            el.set_cmd()

    def run_cmds(self):
        self.set_cmds()
        # print(len(self.cmd_lst[self.cmd[0]]))
        # print(len(self.window.list_panes()))
        # print(self.window.list_panes())
        for index, pane in enumerate(self.window.list_panes()):
            self.select_pane(index)
            self.pane.send_keys(f'{self.cmd_lst[self.cmd[0]][index].cmd}', enter=True)
        pass

    def attach(self):
        self.session.attach_session()

    def exit(self):
        self.session.kill_session()
        # try:
        #     self.session.kill_session()
        # except libtmux.exc.LibTmuxException:
        #     pass

    def purge_sessions(self):
        logit.info(f'killing all sessions matching {self.orig_session_name}')
        server = libtmux.Server()
        try:
            for session in server.list_sessions():
                print(f"session stuff: {str(session)}")
                print(self.session_name, str(session))
                if self.orig_session_name in str(session):
                    print(f"Killing session: {session}")
                    logit.debug(f"Killing session: {session}")
                    session.kill_session()
        except libtmux.exc.LibTmuxException:
            print('No sessions to close... exiting')
            logit.debug('No sessions to close... exiting')

    def smart_grid(self):
        #based on the cmds for the window, set the panes up
        pass

    def select_cmd_index(self, index):
        self.cmd_index = index

        



tnt = TaskWarriorTmux('TaskWarrior')

rows, columns = os.popen('stty size', 'r').read().split()
window_x = int(columns)
window_y = int(rows)
if window_x <= 200:
    grid_x, grid_y = 2,2
    tnt.create_grid(grid_x, grid_y)
    tnt.resize_pane(2,window_x/grid_x,5)
    tnt.close_pane(3)
elif window_x > 200:
    grid_x, grid_y = 3,2
    tnt.create_grid(grid_x, grid_y)
    tnt.resize_pane(3,window_x/grid_x,5)
    tnt.close_pane(4)
else:
    grid_x, grid_y = 1, 1
    tnt.create_grid(grid_x, grid_y)
    tnt.resize_pane(1,window_x/grid_x,5)



# tnt.create_window()
window_cnt = 0



if not any([True for i in [args.p, args.t, args.pri, args.set] if i != None]):
    args.set = ['0']

if args.set[0] == '0':
    
    # Pane 0
    pane = 0
    tnt.cmd_lst[window_cnt][pane].andpriority('H')
    tnt.cmd_lst[window_cnt][pane].andpriority('H')

    # Pane 1
    pane = 1
    tnt.cmd_lst[window_cnt][pane].ortag('learn')
    tnt.cmd_lst[window_cnt][pane].ortag('code')

    # Pane 2
    pane = 2
    tnt.cmd_lst[window_cnt][pane].nottag('code')
    tnt.cmd_lst[window_cnt][pane].nottag('learn')

    # # Pane 3
    # pane = 3
    # tnt.cmd_lst[window_cnt][pane].mark_empty()

    # # Pane 4
    # pane = 4
    # tnt.cmd_lst[window_cnt][pane].mark_empty()
    # tnt.select_pane(1)


# tnt.set_cmds()
tnt.run_cmds()

# for index, c in enumerate(tnt.cmd_lst[0]):
#     print(c.__dict__)
#     print(c.cmd)

# for index, pane in enumerate(tnt.window.list_panes()):
#     pane.send_keys(f'{tnt.cmd_lst[tnt.cmd[0]][index].cmd}', enter=False)
    
if args.killall:
    tnt.purge_sessions()
    exit()

print(args)
if args.attatch:
    tnt.attach()
if args.exit:
    tnt.exit()
exit()

# cmds = []
# cmd_watch = f'sh {working_directory}sim_watch.sh '
# if args.set != None:
#     if args.set[0] == '0':
#         # Primary
#         tnt.panes[0].append[
#             tnt.noproject(''),
#             tnt.nottag('learn'),
#             tnt.nottag('code'),
#             tnt.andpriority('H'),
#             tnt.orpriority('M'),
#         ]
        



#         # tnt.andproject('ica-migration')
#         # tnt.orproject('reports')
#         # tnt.andproject('tester')


#         # tnt.nottag('tagname')
#         # tnt.andtag('tagname')
#         # tnt.ortag('tagname')
#         # tnt.notag('tagname')


#         # tnt.nopriority('whatever')

#         # tnt.orstatus('pending')
#         # tnt.andstatus('pending')
#         # tnt.orstatus('pending')
#         # # tnt.nostatus('pending')





# print(cmds)
# rows, columns = os.popen('stty size', 'r').read().split()
# pane_count_x = int(columns)
# pane_count_y = int(rows)

# # Set number of panes and cmds that will go in each one
# if pane_count_x <= 90:
#     """Expecting a 1x2 grid
#     [ ]
#     [ ]
#     """
#     tnt.create_grid(0,1,2)


# elif pane_count_x > 90 and pane_count_x <= 202:
#     """Expecting a 2x2 grid
#     [][]
#     [  ]
#     """
#     tnt.create_grid(0,2,2)

# else:
#     tnt.create_grid(0,3,2)




# print(tnt.projects)
# print(tnt.tags)
# print(tnt.priorities)
# print(tnt.status)

# if args.killall:
#     tnt.purge_sessions()
#     exit()

# print(args)
# if args.attatch:
#     tnt.attach()
# if args.exit:
#     tnt.exit()
# exit()


# session_name = 'TaskWarrior'
# window_name = session_name

# def _update_name(session_name, count = 0):
#     session_name = list(session_name)
#     while True:
#         try:
#             int(session_name[-1])
#         except ValueError:
#             session_name.append(str(count))
#             return ''.join(session_name), count
#         else:
#             session_name.pop(-1)
#             count += 1

# def create_session(session_name):
#     server = libtmux.Server()
#     count = 0
#     while True:
#         try:
#             session = server.new_session(session_name)
#             break
#         except libtmux.exc.TmuxSessionExists:
#             session_name, count = _update_name(session_name, count)
#     window = session.new_window()
#     # window.rename_window(window_name)
#     window.cmd('rename-window', '-t', window_name)
#     return server, session, window

# def create_grid(window, x=1, y=1):
#     """Create the rows"""
#     for j in range(y-1):
#         window.cmd('split-window', '-v')
#     """Create the columns"""
#     for j in range(y):
#         pane_number = j * x
#         window.cmd('select-pane', '-t', str(pane_number))
#         for i in range(x-1):
#             window.cmd('split-window', '-h')
#     """Itterate through and resize"""
#     rows, columns = os.popen('stty size', 'r').read().split()
#     pane_x = int(columns)
#     pane_y = int(rows)
#     for p in range(x * y):
#         # If we are on the right or bottom edge we dont want to re-size the dimentions of the pane
#         if (p+1) % x == 0:
#             right_side = False
#         else:
#             right_side = True
#         if p >= x*y-x:
#             bottom_side = False
#         else:
#             bottom_side = True

#         window.cmd('select-pane', '-t', str(p))
#         if right_side:
#             window.cmd('resize-pane', '-x', str(pane_x // x))
#         if bottom_side:
#             window.cmd('resize-pane', '-y', str(pane_y // y))
#         # window.cmd('send-keys', f'echo {p}', 'C-m')

# def set_cmd(cmd_lst):
#     cmd_lst.insert(0,'task')
#     if len(cmd_lst) == 0:
#         return'"task"'
#     elif len(cmd_lst) == 1:
#         new_cmd = '"task ' + cmd_lst[0] + '"'
#         return ''.join(new_cmd)
#     else:
#         new_cmd = '"task ' + ' and '.join(cmd_lst) + '"'
#         return ''.join(new_cmd)
#     return ' '.join(cmd_lst)


# def regular_task_warrior():
#     rows, columns = os.popen('stty size', 'r').read().split()
#     pane_x = int(columns)
#     pane_y = int(rows)

#     # Set number of panes and cmds that will go in each one
#     if pane_x <= 202:
#         """Expecting a 2x2 grid
#         [][]
#         [  ]
#         """

#         # Setting up the grid
#         x, y = 2, 2
#         create_grid(window, x, y)
#         pane_number = x*y
#         # Deletign extra pane to make room for more cmd space at the bottom
#         window.cmd('select-pane', '-t', str(pane_number))
#         window.cmd('send-keys', 'exit', 'C-m')

#         # Setting commands run in the main (aux) panes
#         cmd_watch = f'sh {working_directory}sim_watch.sh '
#         cmd_aux0 = []
#         cmd_aux1 = []

#         if args.p == None:
#             pass
#             # ica-migration
#             # testingthis
#             # thosotherproject
#         elif len(args.p) == 1:
#             cmd_aux0.append(f'project:{args.p[0]}')
#         else:
#             cmd_aux0.append(f'project:{args.p[0]}')
#             cmd_aux1.append(f'project:{args.p[1]}')

#         if args.t == None:
#             pass
#             # code
#             # ose
#             # learn
#         elif len(args.t) == 1:
#             cmd_aux0.append(f'tag:{args.t[0]}')
#         else:
#             cmd_aux0.append(f'tag:{args.t[0]}')
#             cmd_aux1.append(f'tag:{args.t[1]}')

#         if args.pri == None:
#             cmd_aux1.append('priority:H or priority:M')
#             # H
#             # M
#         elif len(args.pri) == 1:
#             cmd_aux0.append(f'priority:{args.pri[0]}')
#             cmd_aux1.append('priority:H or priority:M')
#         else:
#             cmd_aux0.append(f'priority:{args.pri[0]}')
#             cmd_aux1.append(f'priority:{args.pri[1]}')

#         cmd_aux0 = set_cmd(cmd_aux0)
#         cmd_aux1 = set_cmd(cmd_aux1)

#         # Running cmds in each pane
#         window.cmd('select-pane', '-t', str(0))
#         window.cmd('send-keys', cmd_watch + cmd_aux0, 'C-m')
#         window.cmd('select-pane', '-t', str(1))
#         window.cmd('send-keys', cmd_watch + cmd_aux1, 'C-m')

#         # Resize the bottom pane to be smaller for cmd entry
#         window.cmd('select-pane', '-t', str(pane_number-2))
#         window.cmd('resize-pane', '-y', str(5))

#         # Select the second to last pane for actual cmd entry
#         window.cmd('select-pane', '-t', str(pane_number-2))

#     else:
#         """Expecting a 3x2 grid
#         [][][]
#         [  ][]
#         """

#         # Setting up the grid
#         x, y = 3, 2
#         create_grid(window, x, y)
#         pane_number = x*y
#         # Deletign extra pane to make room for more cmd space at the bottom
#         window.cmd('select-pane', '-t', str(pane_number-2))
#         window.cmd('send-keys', 'exit', 'C-m')

#         # Setting commands run in the main (aux) panes
#         cmd_watch = f'sh {working_directory}sim_watch.sh '
#         cmd_aux0 = []
#         cmd_aux1 = []
#         cmd_aux2 = []

#         if args.p == None:
#             pass
#             # ica-migration
#             # testingthis
#             # thosotherproject
#         elif len(args.p) == 1:
#             cmd_aux0.append(f'project:{args.p[0]}')
#         elif len(args.p) == 2:
#             cmd_aux0.append(f'project:{args.p[0]}')
#             cmd_aux1.append(f'project:{args.p[1]}')
#         else:
#             cmd_aux0.append(f'project:{args.p[0]}')
#             cmd_aux1.append(f'project:{args.p[1]}')
#             cmd_aux2.append(f'project:{args.p[2]}')

#         if args.t == None:
#             cmd_aux1.append(f'tag:code or tag:learn')
#             # code
#             # ose
#             # learn
#         elif len(args.t) == 1:
#             cmd_aux0.append(f'tag:{args.t[0]}')
#         elif len(args.t) == 2:
#             cmd_aux0.append(f'tag:{args.t[0]}')
#             cmd_aux1.append(f'tag:{args.t[1]}')
#         else:
#             cmd_aux0.append(f'tag:{args.t[0]}')
#             cmd_aux1.append(f'tag:{args.t[1]}')
#             cmd_aux2.append(f'tag:{args.t[2]}')

#         if args.pri == None:
#             cmd_aux2.append('priority:H or priority:M')
#             # H
#             # M
#         elif len(args.pri) == 1:
#             cmd_aux0.append(f'priority:{args.pri[0]}')
#             cmd_aux2.append('priority:H or priority:M')
#         elif len(args.pri) == 2:
#             cmd_aux0.append(f'priority:{args.pri[0]}')
#             cmd_aux1.append(f'priority:{args.pri[1]}')
#             cmd_aux2.append('priority:H or priority:M')
#         else:
#             cmd_aux0.append(f'priority:{args.pri[0]}')
#             cmd_aux1.append(f'priority:{args.pri[1]}')
#             cmd_aux2.append(f'priority:{args.pri[2]}')

#         cmd_aux0 = set_cmd(cmd_aux0)
#         cmd_aux1 = set_cmd(cmd_aux1)
#         cmd_aux2 = set_cmd(cmd_aux2)

#         # Running cmds in each pane
#         window.cmd('select-pane', '-t', str(0))
#         window.cmd('send-keys', cmd_watch + cmd_aux0, 'C-m')
#         window.cmd('select-pane', '-t', str(1))
#         window.cmd('send-keys', cmd_watch + cmd_aux1, 'C-m')
#         window.cmd('select-pane', '-t', str(2))
#         window.cmd('send-keys', cmd_watch + cmd_aux2, 'C-m')

#         # Resize the bottom pane to be smaller for cmd entry
#         window.cmd('select-pane', '-t', str(pane_number-3))
#         window.cmd('resize-pane', '-y', str(5))

#         # Select the second to last pane for actual cmd entry
#         window.cmd('select-pane', '-t', str(pane_number-3))


# def exit_session(sesson):
#     try:
#         session.kill_session()
#     except libtmux.exc.LibTmuxException:
#         pass

# if args.killall:
#     logit.info(f'killing all sessions matching {session_name}')
#     server = libtmux.Server()
#     try:
#         for session in server.list_sessions():
#             if session_name in str(session):
#                 print(f"Killing session: {session}")
#                 logit.debug(f"Killing session: {session}")
#                 session.kill_session()
#     except libtmux.exc.LibTmuxException:
#         print('No sessions to close... exiting')
#         logit.debug('No sessions to close... exiting')
#     exit()

# # # Assign the different window commands
# # if args.p == None:
# #     args.p = []
# # if args.t == None:
# #     args.t = []
# # if args.p == None:
# #     args.pri = []
# # cmds = [
# #     [],
# #     [],
# #     [],
# #     [],
# #     [],
# #     [],
# # ]
# # cmd_watch = f'sh {working_directory}sim_watch.sh '

# # if args.p == None and args.t == None and args.pri == None:
# #     pass
# # # flowtw -p reports,ica-migration -t learn,~code -p '' -t '' -p ica-migration -t code -pri '' -pri '' -pri '' -pri H -pri h,m

# # # flowtw -p '' -t '' -pri '' -p '' -t '' -pri '' -p '' -t '' -pri '' -p '' -t '' -pri '' -p '' -t '' -pri ''

# # if args.p != None:
# #     # ica-migration
# #     # testingthis
# #     # thosotherproject
# #     for index, arg in enumerate(args.p):
# #         if arg in ['']:
# #             continue 
# #         elif arg in ['None']:
# #             cmds[index].append(f"project:")
# #         else:
# #             new_lst = arg.split(',')
# #             cmds[index].append(f"project:{' or project:'.join(new_lst)}")

# # if args.t != None:
# # #     # code
# # #     # ose
# # #     # learn
# #     for index, arg in enumerate(args.t):
# #         if arg in ['']:
# #             continue
# #         if arg in ['None']:
# #             cmds[index].append(f"tag:")
# #         else:
# #             new_lst = []
# #             for newarg in arg.split(','):
# #                 if newarg.startswith('~'):
# #                     new_lst.append(f"-{newarg[1:]}")
# #                 else:
# #                     new_lst.append(f"+{newarg}")
# #             cmds[index].append(f"{' or '.join(new_lst)}")

# # if args.pri != None:
# # #     # H
# # #     # M
# #     # new_lst = []
# #     for index, arg in enumerate(args.pri):
# #         if arg in ['']:
# #             continue
# #         if arg in ['None']:
# #             cmds[index].append(f"priority:")
# #         else:
# #             new_lst = [e.upper() for e in arg.split(',')]
# #             cmds[index].append(f"priority:{' or priority:'.join(new_lst)}")

# # if args.set != None:
# #     print('is a set')
# #     if args.set[0] == '1':
# #         cmds = [
# #             ','
# #         ]
# #         print('one')
# #     else:
# #         print('none')



# # # elif len(args.p) == 1:
# # #     cmd_aux0.append(f'project:{args.p[0]}')
# # # elif len(args.p) == 2:
# # #     cmd_aux0.append(f'project:{args.p[0]}')
# # #     cmd_aux1.append(f'project:{args.p[1]}')
# # # else:
# # #     cmd_aux0.append(f'project:{args.p[0]}')
# # #     cmd_aux1.append(f'project:{args.p[1]}')
# # #     cmd_aux2.append(f'project:{args.p[2]}')

# # # if args.t == None:
# # #     cmd_aux1.append(f'tag:code or tag:learn')

# # # elif len(args.t) == 1:
# # #     cmd_aux0.append(f'tag:{args.t[0]}')
# # # elif len(args.t) == 2:
# # #     cmd_aux0.append(f'tag:{args.t[0]}')
# # #     cmd_aux1.append(f'tag:{args.t[1]}')
# # # else:
# # #     cmd_aux0.append(f'tag:{args.t[0]}')
# # #     cmd_aux1.append(f'tag:{args.t[1]}')
# # #     cmd_aux2.append(f'tag:{args.t[2]}')

# # # if args.pri == None:
# # #     cmd_aux2.append('priority:H or priority:M')

# # # elif len(args.pri) == 1:
# # #     cmd_aux0.append(f'priority:{args.pri[0]}')
# # #     cmd_aux2.append('priority:H or priority:M')
# # # elif len(args.pri) == 2:
# # #     cmd_aux0.append(f'priority:{args.pri[0]}')
# # #     cmd_aux1.append(f'priority:{args.pri[1]}')
# # #     cmd_aux2.append('priority:H or priority:M')
# # # else:
# # #     cmd_aux0.append(f'priority:{args.pri[0]}')
# # #     cmd_aux1.append(f'priority:{args.pri[1]}')
# # #     cmd_aux2.append(f'priority:{args.pri[2]}')

# # # cmd_aux0 = set_cmd(cmd_aux0)
# # # cmd_aux1 = set_cmd(cmd_aux1)
# # # cmd_aux2 = set_cmd(cmd_aux2)
# # exit()
# # for cmd in cmds:
# #     print(set_cmd(cmd))
# #     print(cmd)


# # exit()

# server, session, window = create_session(session_name)
# regular_task_warrior()
# if args.attatch:
#     session.attach_session()
# if args.exit:
#     exit_session(session)




# # import libtmux
# # import math
# # import os
# # import logging

# # def create_session(session_name, commands):
# #     '''
# #     create session with 2*2 panes and run commands
# #     :param session_name: tmux session name
# #     :param commands: bash commands
# #     :return:
# #     '''
# #     logging.info(commands)
# #     # pane_NUM = 3
# #     # WINDOW_NUM = int(math.ceil(len(commands)/4.0))  # in python3, we can use 4 also

# #     server = libtmux.Server()
# #     session = server.new_session(session_name)

# #     # create windows
# #     windows = []
# #     panes = []

# #     for i in range(len(commands)):
# #         # create window to store 4 panes
# #         if i % 4 == 0:
# #             win = session.new_window(attach=False, window_name="win"+str(int(i/4)))
# #             windows.append(win)

# #             # tmux_args = ('-h',)
# #             win.cmd('split-window', '-h')
# #             win.cmd('split-window', '-f')
# #             win.cmd('split-window', '-h')

# #             panes.extend(win.list_panes())

# #         panes[i].send_keys(commands[i])

# #     logging.info(panes)
# #     logging.info(windows)


# # if __name__ == '__main__':
# #     commands = []
# #     for i in range(10):
# #         commands.append("echo " + str(i))

# #     os.system("tmux kill-session -t session")
# #     create_session("session", commands)
