import sublime
import sublime_plugin
import threading
import subprocess
import os
import glob
import os.path

from functools import partial
SETTINGS_FILE = "DjangoCommands.sublime-settings"

def log(message):
    print(' - Django: ' + message)

def read_settings():
    settings = sublime.load_settings(SETTINGS_FILE)
    python_bin = settings.get('python_bin')
    log('Python path is ' + python_bin)
    manage_py = find_manage_py()
    if manage_py is None:
        manage_py = settings.get('manage_py')
    
    return (python_bin, manage_py)

def find_manage_py():
    name = u'manage.py'
    for path in sublime.active_window().folders():
        for walk in os.walk(path):    
            if name in walk[2]:
                log('Found manage.py in ' + walk[0])
                return os.path.join(walk[0], name)


class DjangoCommand(sublime_plugin.WindowCommand):
    def run_command(self, command):
        python_bin, manage_py = read_settings()    
        thread = CommandThread(command, python_bin, manage_py)
        thread.start()


class DjangoRunCommand(DjangoCommand):

    def run(self):
        self.run_command(['runserver'])


class DjangoSyncdbCommand(DjangoCommand):

    def run(self):
        self.run_command(['syncdb'])


class DjangoMigrateCommand(DjangoCommand):

    def run(self):
        self.run_command(['migrate'])


class DjangoCustomCommand(DjangoCommand):  
    
    def run(self):
        self.window.show_input_panel("Django manage.py command", "",
                                     self.on_input, None, None)

    def on_input(self, command):
        command = str(command)  # avoiding unicode
        if command.strip() == "":        
            return
        import shlex
        command_splitted = shlex.split(command)
        log(command_splitted)
        self.run_command(command_splitted)


class SetVirtualEnvCommand(DjangoCommand):

    def scan_for_virtualenvs(self, venv_paths):
        bin_dir = "Scripts" if os.name == "nt" else "bin"
        found_dirs = set()
        for venv_path in venv_paths:
            p = os.path.expanduser(venv_path)
            pattern = os.path.join(p, "*", bin_dir, "activate_this.py")
            found_dirs.update(list(map(os.path.dirname, glob.glob(pattern))))
        return sorted(found_dirs)

    def _scan(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        return self.scan_for_virtualenvs(venv_paths)

    def set_virtualenv(self, choices, index):
        if index == -1:
            return
        (name, directory) = choices[index]
        log('Virtual environment "' + name + '" is set')
        self.settings.set("python_bin", os.path.join(directory, 'python'))        
        sublime.save_settings(SETTINGS_FILE)

    def run(self):
        self.settings = sublime.load_settings(SETTINGS_FILE)
        choices = self._scan()
        nice_choices = [[path.split(os.path.sep)[-2], path] for path in choices]
        on_input = partial(self.set_virtualenv, nice_choices)
        self.window.show_quick_panel(nice_choices, on_input)


class CommandThread(threading.Thread):

    def __init__(self, action, python, manage_py):
        self.python = python
        self.manage_py = manage_py
        self.action = action
        threading.Thread.__init__(self)

    def run(self):
        import platform
        command = [self.python, self.manage_py] + self.action
        if platform.system() == 'Windows':
            command = ["cmd.exe", "/k"] + command
        log('Command is : ' + str(command))
        subprocess.Popen(command)
        