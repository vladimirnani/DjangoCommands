import sublime
import sublime_plugin
import threading
import subprocess
import os


def read_settings():
    settings = sublime.load_settings("DjangoCommands.sublime-settings")
    python_bin = settings.get('python_bin')
    print python_bin
    manage_py = find_manage_py()
    if manage_py is None:
        manage_py = settings.get('manage_py')
    
    return (python_bin, manage_py)

def find_manage_py():
    name = 'manage.py'
    for path in sublime.active_window().folders():
        for walk in os.walk(path):           
            if name in walk[1]:
                return os.path.join(walk[0], name)


class DjangoCommand(sublime_plugin.WindowCommand):
    def run_command(self, command, use_terminal=False):
        python_bin, manage_py = read_settings()    
        thread = CommandThread(command, python_bin, manage_py, use_terminal)
        thread.start()


class DjangoRunCommand(DjangoCommand):

    def run(self):
        self.run_command(['runserver'], True)


class DjangoSyncdbCommand(DjangoCommand):

    def run(self):
        self.run_command(['syncdb'])


class DjangoMigrateCommand(DjangoCommand):

    def run(self):
        self.run_command(['migrate'])


class DjangoCustomCommand(DjangoCommand):  
    
    def run(self):
        self.window.show_input_panel("Django manage command", "",
                                     self.on_input, None, None)

    def on_input(self, command):
        command = str(command)  # avoiding unicode
        if command.strip() == "":        
            return
        import shlex
        command_splitted = shlex.split(command)
        print command_splitted
        self.run_command(command_splitted, True)


class CommandThread(threading.Thread):

    def __init__(self, action, python, manage_py, use_terminal):
        self.python = python
        self.manage_py = manage_py
        self.action = action
        self.use_terminal = use_terminal
        threading.Thread.__init__(self)

    def run_and_output_to_terminal(self, command):
        subprocess.Popen(command)
       
    def run(self):
        import platform
        command = [self.python, self.manage_py] + self.action
        if platform.system() == 'Windows':
            command = ["cmd.exe", "/k"] + command
        print command
        self.run_and_output_to_terminal(command)
        