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
  
    def run_command(self, action, use_terminal=False):
        python_bin, manage_py = read_settings()    
        thread = CommandThread(action, python_bin, manage_py, use_terminal)
        thread.start()


class DjangoRunCommand(DjangoCommand):

    def run(self):
        self.run_command('runserver', True)


class DjangoSyncdbCommand(DjangoCommand):

    def run(self):
        self.run_command('syncdb')


class DjangoMigrateCommand(DjangoCommand):

    def run(self):
        self.run_command('migrate')


class CommandThread(threading.Thread):

    def __init__(self, action, python, manage_py, use_terminal):
        self.python = python
        self.manage_py = manage_py
        self.action = action
        self.use_terminal = use_terminal
        threading.Thread.__init__(self)

    @classmethod
    def speak_output(cls, lines, errlines):
        for line in errlines:
            print line

        for line in lines:
            print line


    def run_and_output_to_terminal(self, command):
        subprocess.Popen(command)
        

    def run_and_output_to_sublime(self, command):
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                shell=True)
        output, eoutput = proc.communicate()

        lines = [line for line in output.split('\n')]
        elines = [line for line in eoutput.split('\n')]

        sublime.set_timeout(lambda: self.speak_output(lines, elines), 500)


    def run(self):
        command = [self.python, self.manage_py, self.action]
        print command
        if self.use_terminal:
            self.run_and_output_to_terminal(command)
        else:
            self.run_and_output_to_sublime(command)

