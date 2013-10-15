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


class SimpleDjangoCommand(DjangoCommand):
    command = ''

    def run(self):
        self.run_command([self.command])


class DjangoRunCommand(SimpleDjangoCommand):
    command = 'runserver'


class DjangoSyncdbCommand(SimpleDjangoCommand):
    command = 'syncdb'


class DjangoShellCommand(SimpleDjangoCommand):
    command = 'shell'


class DjangoTestCommand(SimpleDjangoCommand):
    command = 'test'


class DjangoMigrateCommand(SimpleDjangoCommand):
    command = 'migrate'


class DjangoSchemaMigrationCommand(DjangoCommand):

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
        self.run_command(['schemamigration', name, '--auto'])

    def run(self):
        choices = self.scan_for_apps()
        nice_choices = [[path.split(os.path.sep)[-2], path] for path in choices]
        on_input = partial(self.app_choose, nice_choices)
        self.window.show_quick_panel(nice_choices, on_input)


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
        import shlex
        command_splitted = shlex.split(command)
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
        if platform.system() == 'Linux':
            string_command = 'bash -c \"'
            for arg in command:
                string_command += arg
                string_command += ' '
            string_command += '; read line\"'
            command = ["gnome-terminal", "-e", string_command]
        log('Command is : ' + str(command))  
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

