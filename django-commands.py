import sublime
import sublime_plugin
import threading
import subprocess
import os
import glob
import platform
import shlex
from functools import partial

SETTINGS_FILE = 'DjangoCommands.sublime-settings'
PLATFORM = platform.system()

def log(message):
    print(' - Django: {0}'.format(message))


class DjangoCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args, **kwargs):
        self.settings = sublime.load_settings(SETTINGS_FILE)
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)


    def find_manage_py(self):
        for path in sublime.active_window().folders():
            for root, dirs, files in os.walk(path):
                if 'manage.py' in files:
                    return os.path.join(root, 'manage.py')

    def prettify(self, app_dir, base_dir):
        name = app_dir.replace(base_dir, '')
        name = name.replace(self.app_descriptor, '')
        name = name[1:-1]
        name = name.replace(os.path.sep, '.')
        return name

    def choose(self, choices, action):
        base_dir = os.path.dirname(self.find_manage_py())
        nice_choices = [self.prettify(path, base_dir) for path in choices]
        on_input = partial(action, nice_choices)
        self.window.show_quick_panel(nice_choices, on_input)

    def run_command(self, command):
        bin = self.settings.get('python_bin')
        manage_py = self.settings.get('manage_py') or self.find_manage_py()

        base_dir = os.path.abspath(os.path.join(manage_py, os.pardir))
        os.chdir(base_dir)

        command = [bin, manage_py] + command

        thread = CommandThread(command)
        thread.start()


class CommandThread(threading.Thread):

    def __init__(self, command):
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        command = ' '.join(self.command)

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


class SimpleDjangoCommand(DjangoCommand):
    command = ''

    def run(self):
        self.run_command([self.command])


class DjangoAppCommand(DjangoCommand):
    command = ''
    extra_args = []
    app_descriptor = 'models.py'

    def find_apps(self):
        apps = set()
        for project_folder in sublime.active_window().folders():
            dirs = [x[0] for x in os.walk(project_folder)]
            for dir in dirs:
                dir = os.path.expanduser(dir)
                pattern = os.path.join(dir, "*", self.app_descriptor)
                apps.update(list(map(lambda x: x, glob.glob(pattern))))
        return sorted(apps)

    def choose_app(self, apps, index):
        if index == -1:
            return
        name = apps[index]
        self.run_command([self.command, name] + self.extra_args)

    def run(self):
        choices = self.find_apps()
        self.choose(choices, self.choose_app)


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


class DjangoTestAllCommand(SimpleDjangoCommand):
    command = 'test'


class DjangoTestAppCommand(DjangoAppCommand):
    command = 'test'
    app_descriptor = 'tests.py'


class DjangoSchemaMigrationCommand(DjangoAppCommand):
    command = 'schemamigration'
    extra_args = ['--auto']


class DjangoListMigrationsCommand(SimpleDjangoCommand):
    command = 'migrate'
    extra_args = ['--list']


class DjangoCustomCommand(DjangoCommand):

    def run(self):
        self.window.show_input_panel("Django manage.py command",
                                     "", self.on_input, None, None)

    def on_input(self, command):
        log(str(command))
        command = str(command)
        if command.strip() == "":
            return
        command_splitted = shlex.split(command)
        self.run_command(command_splitted)


class TerminalHereCommand(DjangoCommand):

    def run(self):
        bin = self.settings.get('python_bin')
        manage_py = self.settings.get('manage_py') or self.find_manage_py()

        base_dir = os.path.abspath(os.path.join(manage_py, os.pardir))
        os.chdir(base_dir)

        command = [os.path.join(os.path.dirname(bin), 'activate')]

        thread = CommandThread(command)
        thread.start()


class SetVirtualEnvCommand(DjangoCommand):

    def find_virtualenvs(self, venv_paths):
        bin = "Scripts" if PLATFORM == 'Windows' else "bin"
        venvs = set()
        for path in venv_paths:
            path = os.path.expanduser(path)
            pattern = os.path.join(path, "*", bin, "activate_this.py")
            venvs.update(list(map(os.path.dirname, glob.glob(pattern))))
        return sorted(venvs)

    def set_virtualenv(self, venvs, index):
        if index == -1:
            return
        name, directory = venvs[index]
        log('Virtual environment "{0}" is set'.format(name))
        interpreter = os.path.join(directory, 'python')
        self.settings.set("python_bin", interpreter)
        sublime.save_settings(SETTINGS_FILE)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        choices = self.find_virtualenvs(venv_paths)
        self.choose(choices, self.set_virtualenv)
