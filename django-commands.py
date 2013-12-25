import sublime
import sublime_plugin
import threading
import subprocess
import os
import glob
import os.path
import platform
import shlex
from functools import partial

SETTINGS_FILE = 'DjangoCommands.sublime-settings'
PLATFORM = platform.system()

def log(message):
    print(' - Django: {0}'.format(message))


def find_manage_py():
    name = u'manage.py'
    for path in sublime.active_window().folders():
        for walk in os.walk(path):
            files = walk[2]
            if name in files:
                folder = walk[0]
                log('Found manage.py in {0}'.format(folder))
                return os.path.join(folder, name)


class DjangoCommand(sublime_plugin.WindowCommand):
    settings = sublime.load_settings(SETTINGS_FILE)

    def read_settings(self):
        python_bin = self.settings.get('python_bin')
        log('Python path is ' + python_bin)
        manage_py = find_manage_py() or self.settings.get('manage_py')
        return (python_bin, manage_py)

    def run_command(self, command):
        python_bin, manage_py = self.read_settings()
        thread = CommandThread(command, python_bin, manage_py)
        thread.start()


class SimpleDjangoCommand(DjangoCommand):
    command = ''

    def run(self):
        self.run_command([self.command])


class DjangoAppCommand(DjangoCommand):
    command = ''
    extra_args = []

    def scan_for_apps(self):
        found_dirs = set()
        for project_folder in sublime.active_window().folders():
            folders = [x[0] for x in os.walk(project_folder)]
            for folder in folders:
                p = os.path.expanduser(folder)
                pattern = os.path.join(p, "*", "models.py")
                found_dirs.update(list(map(lambda x: x, glob.glob(pattern))))
        return sorted(found_dirs)

    def app_choose(self, choices, index):
        if index == -1:
            return
        (name, directory) = choices[index]
        self.run_command([self.command, name] + self.extra_args)

    def run(self):
        choices = self.scan_for_apps()
        nice_choices = [[path.split(os.path.sep)[-2], path] for path in choices]
        on_input = partial(self.app_choose, nice_choices)
        self.window.show_quick_panel(nice_choices, on_input)



class DjangoRunCommand(SimpleDjangoCommand):
    command = 'runserver'


class DjangoSyncdbCommand(SimpleDjangoCommand):
    command = 'syncdb'


class DjangoShellCommand(SimpleDjangoCommand):
    command = 'shell'


class DjangoCheckCommand(SimpleDjangoCommand):
    command = 'check'


class DjangoHelpCommand(SimpleDjangoCommand):
    command = 'help'


class DjangoMigrateCommand(SimpleDjangoCommand):
    command = 'migrate'


class DjangoSchemaMigrationCommand(DjangoAppCommand):
    command = 'schemamigration'
    extra_args = ['--auto']


class DjangoTestAllCommand(SimpleDjangoCommand):
    command = 'test'


class DjangoTestAppCommand(DjangoAppCommand):
    command = 'test'


class DjangoListMigrationsCommand(DjangoCommand):

    def run(self):
        self.run_command(['migrate', '--list'])


class DjangoCustomCommand(DjangoCommand):

    def run(self):
        self.window.show_input_panel("Django manage.py command", "",
                                     self.on_input, None, None)

    def on_input(self, command):
        command = str(command)
        if command.strip() == "":
            return
        command_splitted = shlex.split(command)
        self.run_command(command_splitted)


class SetVirtualEnvCommand(DjangoCommand):

    def scan_for_virtualenvs(self, venv_paths):
        bin = "Scripts" if PLATFORM == 'Windows' else "bin"
        found_dirs = set()
        for path in venv_paths:
            p = os.path.expanduser(path)
            pattern = os.path.join(p, "*", bin, "activate_this.py")
            found_dirs.update(list(map(os.path.dirname, glob.glob(pattern))))
        return sorted(found_dirs)

    def _scan(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        return self.scan_for_virtualenvs(venv_paths)

    def set_virtualenv(self, choices, index):
        if index == -1:
            return
        (name, directory) = choices[index]
        log('Virtual environment "{0}" is set'.format(name))
        self.settings.set("python_bin", os.path.join(directory, 'python'))
        sublime.save_settings(SETTINGS_FILE)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        choices = self.scan_for_virtualenvs(venv_paths)
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
        command = [self.python, self.manage_py] + self.action
        command = ' '.join(command)

        if PLATFORM == 'Windows':
            command = [
                'cmd.exe',
                '/k', command
            ]
        if PLATFORM == 'Linux':
            command = [
                'gnome-terminal',
                '-e', 'bash -c \"{0}; read line\"'.format(command)
            ]
        if PLATFORM == 'Darwin':
            command = [
                'osascript',
                '-e', 'tell app "Terminal" to activate',
                '-e', 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down',
                '-e', 'tell application "Terminal" to do script "{0}" in front window'.format(command)
            ]

        log('Command is : {0}'.format(str(command)))
        subprocess.Popen(command, shell=False)
