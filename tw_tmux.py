import argparse
import logging
import libtmux
import os

# https://libtmux.git-pull.com/api.html

working_directory = os.environ['HOME'] + f'/premade_tmux/'

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
aparse.add_argument('-kill', action='store_false', help='Find and close session with matching name')
aparse.add_argument('--killall', action='store_true', help='Find and close ALL sessions with matching name')

args = aparse.parse_args()

logit.info(f"args:{args}")


session_name = 'TaskWarrior'
window_name = session_name

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

def create_session(session_name):
    server = libtmux.Server()
    count = 0
    while True:
        try:
            session = server.new_session(session_name)
            break
        except libtmux.exc.TmuxSessionExists:
            session_name, count = _update_name(session_name, count)
    window = session.new_window()
    # window.rename_window(window_name)
    window.cmd('rename-window', '-t', window_name)
    return server, session, window


def create_grid(window, x=1, y=1):
    """Create the rows"""
    for j in range(y-1):
        window.cmd('split-window', '-v')
    """Create the columns"""
    for j in range(y):
        pane_number = j * x
        window.cmd('select-pane', '-t', str(pane_number))
        for i in range(x-1):
            window.cmd('split-window', '-h')
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

        window.cmd('select-pane', '-t', str(p))
        if right_side:
            window.cmd('resize-pane', '-x', str(pane_x // x))
        if bottom_side:
            window.cmd('resize-pane', '-y', str(pane_y // y))
        # window.cmd('send-keys', f'echo {p}', 'C-m')

def set_cmd(cmd_lst):
    if len(cmd_lst) == 0:
        return'"task"'
    elif len(cmd_lst) == 1:
        new_cmd = '"task ' + cmd_lst[0] + '"'
        return ''.join(new_cmd)
    else:
        new_cmd = '"task ' + ' and '.join(cmd_lst) + '"'
        return ''.join(new_cmd)
    return ' '.join(cmd_lst)


def regular_task_warrior():
    rows, columns = os.popen('stty size', 'r').read().split()
    pane_x = int(columns)
    pane_y = int(rows)

    # Set number of panes and cmds that will go in each one
    if pane_x <= 202:
        """Expecting a 2x2 grid
        [][]
        [  ]
        """

        # Setting up the grid
        x, y = 2, 2
        create_grid(window, x, y)
        pane_number = x*y
        # Deletign extra pane to make room for more cmd space at the bottom
        window.cmd('select-pane', '-t', str(pane_number))
        window.cmd('send-keys', 'exit', 'C-m')

        # Setting commands run in the main (aux) panes
        cmd_watch = f'sh {working_directory}sim_watch.sh '
        cmd_aux0 = []
        cmd_aux1 = []

        if args.p == None:
            pass
            # ica-migration
            # testingthis
            # thosotherproject
        elif len(args.p) == 1:
            cmd_aux0.append(f'project:{args.p[0]}')
        else:
            cmd_aux0.append(f'project:{args.p[0]}')
            cmd_aux1.append(f'project:{args.p[1]}')

        if args.t == None:
            pass
            # code
            # ose
            # learn
        elif len(args.t) == 1:
            cmd_aux0.append(f'tag:{args.t[0]}')
        else:
            cmd_aux0.append(f'tag:{args.t[0]}')
            cmd_aux1.append(f'tag:{args.t[1]}')

        if args.pri == None:
            cmd_aux1.append('priority:H or priority:M')
            # H
            # M
        elif len(args.pri) == 1:
            cmd_aux0.append(f'priority:{args.pri[0]}')
            cmd_aux1.append('priority:H or priority:M')
        else:
            cmd_aux0.append(f'priority:{args.pri[0]}')
            cmd_aux1.append(f'priority:{args.pri[1]}')

        cmd_aux0 = set_cmd(cmd_aux0)
        cmd_aux1 = set_cmd(cmd_aux1)

        # Running cmds in each pane
        window.cmd('select-pane', '-t', str(0))
        window.cmd('send-keys', cmd_watch + cmd_aux0, 'C-m')
        window.cmd('select-pane', '-t', str(1))
        window.cmd('send-keys', cmd_watch + cmd_aux1, 'C-m')

        # Resize the bottom pane to be smaller for cmd entry
        window.cmd('select-pane', '-t', str(pane_number-2))
        window.cmd('resize-pane', '-y', str(5))

        # Select the second to last pane for actual cmd entry
        window.cmd('select-pane', '-t', str(pane_number-2))

    else:
        """Expecting a 3x2 grid
        [][][]
        [  ][]
        """

        # Setting up the grid
        x, y = 3, 2
        create_grid(window, x, y)
        pane_number = x*y
        # Deletign extra pane to make room for more cmd space at the bottom
        window.cmd('select-pane', '-t', str(pane_number-2))
        window.cmd('send-keys', 'exit', 'C-m')

        # Setting commands run in the main (aux) panes
        cmd_watch = f'sh {working_directory}sim_watch.sh '
        cmd_aux0 = []
        cmd_aux1 = []
        cmd_aux2 = []

        if args.p == None:
            pass
            # ica-migration
            # testingthis
            # thosotherproject
        elif len(args.p) == 1:
            cmd_aux0.append(f'project:{args.p[0]}')
        elif len(args.p) == 2:
            cmd_aux0.append(f'project:{args.p[0]}')
            cmd_aux1.append(f'project:{args.p[1]}')
        else:
            cmd_aux0.append(f'project:{args.p[0]}')
            cmd_aux1.append(f'project:{args.p[1]}')
            cmd_aux2.append(f'project:{args.p[2]}')

        if args.t == None:
            cmd_aux1.append(f'tag:code or tag:learn')
            # code
            # ose
            # learn
        elif len(args.t) == 1:
            cmd_aux0.append(f'tag:{args.t[0]}')
        elif len(args.t) == 2:
            cmd_aux0.append(f'tag:{args.t[0]}')
            cmd_aux1.append(f'tag:{args.t[1]}')
        else:
            cmd_aux0.append(f'tag:{args.t[0]}')
            cmd_aux1.append(f'tag:{args.t[1]}')
            cmd_aux2.append(f'tag:{args.t[2]}')

        if args.pri == None:
            cmd_aux2.append('priority:H or priority:M')
            # H
            # M
        elif len(args.pri) == 1:
            cmd_aux0.append(f'priority:{args.pri[0]}')
            cmd_aux2.append('priority:H or priority:M')
        elif len(args.pri) == 2:
            cmd_aux0.append(f'priority:{args.pri[0]}')
            cmd_aux1.append(f'priority:{args.pri[1]}')
            cmd_aux2.append('priority:H or priority:M')
        else:
            cmd_aux0.append(f'priority:{args.pri[0]}')
            cmd_aux1.append(f'priority:{args.pri[1]}')
            cmd_aux2.append(f'priority:{args.pri[2]}')

        cmd_aux0 = set_cmd(cmd_aux0)
        cmd_aux1 = set_cmd(cmd_aux1)
        cmd_aux2 = set_cmd(cmd_aux2)

        # Running cmds in each pane
        window.cmd('select-pane', '-t', str(0))
        window.cmd('send-keys', cmd_watch + cmd_aux0, 'C-m')
        window.cmd('select-pane', '-t', str(1))
        window.cmd('send-keys', cmd_watch + cmd_aux1, 'C-m')
        window.cmd('select-pane', '-t', str(2))
        window.cmd('send-keys', cmd_watch + cmd_aux2, 'C-m')

        # Resize the bottom pane to be smaller for cmd entry
        window.cmd('select-pane', '-t', str(pane_number-3))
        window.cmd('resize-pane', '-y', str(5))

        # Select the second to last pane for actual cmd entry
        window.cmd('select-pane', '-t', str(pane_number-3))


def exit_session(sesson):
    try:
        session.kill_session()
    except libtmux.exc.LibTmuxException:
        pass

if args.killall:
    logit.info(f'killing all sessions matching {session_name}')
    server = libtmux.Server()
    try:
        for session in server.list_sessions():
            if session_name in str(session):
                print(f"Killing session: {session}")
                logit.debug(f"Killing session: {session}")
                session.kill_session()
    except libtmux.exc.LibTmuxException:
        print('No sessions to close... exiting')
        logit.debug('No sessions to close... exiting')
    exit()

server, session, window = create_session(session_name)
regular_task_warrior()
if args.attatch:
    session.attach_session()
if args.exit:
    exit_session(session)




# import libtmux
# import math
# import os
# import logging

# def create_session(session_name, commands):
#     '''
#     create session with 2*2 panes and run commands
#     :param session_name: tmux session name
#     :param commands: bash commands
#     :return:
#     '''
#     logging.info(commands)
#     # pane_NUM = 3
#     # WINDOW_NUM = int(math.ceil(len(commands)/4.0))  # in python3, we can use 4 also

#     server = libtmux.Server()
#     session = server.new_session(session_name)

#     # create windows
#     windows = []
#     panes = []

#     for i in range(len(commands)):
#         # create window to store 4 panes
#         if i % 4 == 0:
#             win = session.new_window(attach=False, window_name="win"+str(int(i/4)))
#             windows.append(win)

#             # tmux_args = ('-h',)
#             win.cmd('split-window', '-h')
#             win.cmd('split-window', '-f')
#             win.cmd('split-window', '-h')

#             panes.extend(win.list_panes())

#         panes[i].send_keys(commands[i])

#     logging.info(panes)
#     logging.info(windows)


# if __name__ == '__main__':
#     commands = []
#     for i in range(10):
#         commands.append("echo " + str(i))

#     os.system("tmux kill-session -t session")
#     create_session("session", commands)
