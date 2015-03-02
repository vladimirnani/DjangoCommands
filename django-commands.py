import sublime
import sublime_plugin
import threading
import subprocess
import os
import glob
import platform
import shutil
import re

from functools import partial
from collections import OrderedDict
from urllib.parse import urlencode

SETTINGS_FILE = 'DjangoCommands.sublime-settings'
PLATFORM = platform.system()
LATEST_DJANGO_RELEASE = 1.7
TERMINAL = ''


def log(message):
    print(' - Django: {0}'.format(message))


class DjangoCommand(sublime_plugin.WindowCommand):
    project_true = True

    def __init__(self, *args, **kwargs):
        self.settings = sublime.load_settings(SETTINGS_FILE)
        self.interpreter_versions = {2: "python2",
                                     3: "python3"} if PLATFORM is not "Windows" else {2: "python", 3: "python"}
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)

    def get_manage_py(self):
        return self.settings.get('django_project_root')or self.find_manage_py()

    def get_executable(self):
        self.project_true = self.settings.get('project_override')
        settings_interpreter = self.settings.get('python_bin')
        project = self.window.project_data()
        settings_exists = 'settings' in project.keys()
        if settings_exists and self.project_true:
            project_interpreter = project['settings'].get('python_interpreter')
            if project_interpreter is not None and self.project_true is True:
                self.settings.set('python_bin', project_interpreter)
                return project_interpreter
            elif project_interpreter is not None and self.project_true is False:
                return settings_interpreter
            else:
                version = self.settings.get("python_version")
                return shutil.which(self.interpreter_versions[version])
        elif settings_interpreter is not None:
            return settings_interpreter
        else:
            version = self.settings.get("python_version")
            return shutil.which(self.interpreter_versions[version])

    def find_manage_py(self):
        for path in sublime.active_window().folders():
            for root, dirs, files in os.walk(path):
                if 'manage.py' in files:
                    return os.path.join(root, 'manage.py')

    def choose(self, choices, action):
        on_input = partial(action, choices)
        self.window.show_quick_panel(choices, on_input)

    def go_to_project_home(self):
        try:
            if self.manage_py is None:
                return
        except:
            return
        base_dir = os.path.abspath(os.path.join(self.manage_py, os.pardir))
        os.chdir(base_dir)

    def format_command(self, command):
        binary = self.get_executable()
        self.manage_py = self.get_manage_py()
        self.go_to_project_home()

        command = "{} {} {}".format(binary, self.manage_py, command)
        return command

    def run_command(self, command):
        global TERMINAL
        if PLATFORM == "Linux":
            TERMINAL = self.settings.get('linux_terminal')
            if TERMINAL is None:
                TERMINAL = self.settings.get('linux-terminal', 'gnome-terminal')
        command = self.format_command(command)
        thread = CommandThread(command)
        thread.start()


class CommandThread(threading.Thread):

    def __init__(self, command):
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        command = "{}".format(self.command)
        env = os.environ.copy()
        if PLATFORM == 'Windows':
            command = [
                'cmd.exe',
                '/k', "{} && timeout /T 10 && exit".format(command)
            ]
        if PLATFORM == 'Linux':
            command = [
                TERMINAL,
                '-e', 'bash -c \"{0}; read line\"'.format(command)
            ]
        if PLATFORM == 'Darwin':
            command = [
                'osascript',
                '-e', 'tell app "Terminal" to activate',
                '-e', 'tell application "System Events" to tell process \
                "Terminal" to keystroke "t" using command down',
                '-e', 'tell application "Terminal" to \
                do script "{0}" in front window'.format(command)
            ]

        log('Command is : {0}'.format(str(command)))
        subprocess.Popen(command, env=env)


class DjangoSimpleCommand(DjangoCommand):
    command = ''
    extra_args = []

    def get_command(self):
        return "{} {}".format(self.command, " ".join(self.extra_args))

    def run(self):
        command = self.get_command()
        self.run_command(command)


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

    def prettify(self, app_dir, base_dir):
        name = app_dir.replace(base_dir, '')
        name = name.replace(self.app_descriptor, '')
        name = name[1:-1]
        name = name.replace(os.path.sep, '.')
        return name

    def on_choose_app(self, apps, index):
        if index == -1:
            return
        name = apps[index]
        self.run_command(
            "{} {} {}".format(self.command,
                              "".join(name),
                              " ".join(self.extra_args)))

    def run(self):
        self.go_to_project_home()
        choices = self.find_apps()
        self.manage_py = self.get_manage_py()
        base_dir = os.path.dirname(self.manage_py)
        choices = [self.prettify(path, base_dir) for path in choices]
        self.choose(choices, self.on_choose_app)


class DjangoOtherCommand(DjangoSimpleCommand):

    def get_commands(self):
        forSplit = self.format_command('help --commands')
        command = forSplit.split(' ')
        out = str(subprocess.check_output(command))
        out = re.search('b\'(.*)\'', out).group(1)
        commands = out.split('\\n')[:-1] if PLATFORM is not "Windows" else out.split('\\r\\n')[:-1]
        return commands

    def on_choose_command(self, commands, index):
        if index == -1:
            return
        name = commands[index]
        self.run_command(name)

    def run(self):
        commands = self.get_commands()
        self.choose(commands, self.on_choose_command)


class DjangoRunCommand(DjangoSimpleCommand):
    command = 'runserver'

    def run(self):
        port = self.settings.get('server_port')
        host = self.settings.get('server_host')
        self.extra_args = [host, port]
        inComannd = "{} {}:{}".format(self.command, host, port)
        self.run_command(inComannd)


class DjangoSyncdbCommand(DjangoSimpleCommand):
    command = 'syncdb'


class DjangoShellCommand(DjangoSimpleCommand):
    command = 'shell'


class DjangoDbShellCommand(DjangoSimpleCommand):
    command = 'dbshell'


class DjangoCheckCommand(DjangoSimpleCommand):
    command = 'check'


class DjangoHelpCommand(DjangoSimpleCommand):
    command = 'help'


class DjangoMigrateCommand(DjangoSimpleCommand):
    command = 'migrate'


class DjangoMigrateAppCommand(DjangoAppCommand):
    command = 'migrate'


class DjangoTestAllCommand(DjangoSimpleCommand):
    command = 'test'


class DjangoTestAppCommand(DjangoAppCommand):
    command = 'test'
    app_descriptor = 'tests.py'


class DjangoMakeMigrationCommand(DjangoSimpleCommand):
    command = 'makemigrations'


class DjangoInitialSchemaMigrationCommand(DjangoAppCommand):
    command = 'schemamigration'
    extra_args = ['--initial']


class DjangoSchemaMigrationCommand(DjangoAppCommand):
    command = 'schemamigration'
    extra_args = ['--auto']


class DjangoListMigrationsCommand(DjangoSimpleCommand):
    command = 'migrate'
    extra_args = ['--list']


class DjangoSqlMigrationCommand(DjangoAppCommand):
    command = 'sqlmigrate'

    def set_migration_name(self, name):
        self.extra_args = [name]
        DjangoAppCommand.run(self)

    def run(self):
        self.window.show_input_panel(
            "Migration name", "", self.set_migration_name, None, None)


class DjangoCustomCommand(DjangoCommand):

    def run(self):
        caption = "Django manage.py command"
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, command):
        command = command
        if command.strip() == '':
            return
        self.run_command(command)


class VirtualEnvCommand(DjangoCommand):
    command = ''
    extra_args = []

    def is_enabled(self):
        return self.settings.get('python_bin') is not None

    def run(self):
        self.manage_py = self.get_manage_py()
        self.go_to_project_home()
        bin_dir = os.path.dirname(self.settings.get('python_bin'))
        command = "{} {}".format(
            os.path.join(bin_dir, self.command), " ".join(self.extra_args))
        thread = CommandThread(command)
        thread.start()


class TerminalHereCommand(VirtualEnvCommand):
    command = 'activate'

    def run(self):
        self.manage_py = self.get_manage_py()
        self.go_to_project_home()
        bin_dir = os.path.dirname(self.settings.get('python_bin'))
        if PLATFORM == 'Windows':
            command = 'cmd /k {}'.format(
                os.path.join(bin_dir, self.command))
        if PLATFORM == 'Linux' or PLATFORM == 'Darwin':
            command = "bash --rcfile <(echo '. ~/.bashrc && . {}')".format(
                os.path.join(bin_dir, self.command))
        thread = CommandThread(command)
        thread.start()


class PipFreezeCommand(VirtualEnvCommand):
    command = 'pip'
    extra_args = ['freeze']


class PipFreezeToFileCommand(VirtualEnvCommand):
    command = 'pip'
    extra_args = ['freeze']

    def on_done(self, filename):
        self.extra_args.append('>')
        self.extra_args.append(filename)
        VirtualEnvCommand.run(self)

    def run(self):
        self.window.show_input_panel(
            "File name", "requirements.txt", self.on_done, None, None)


class PipInstallRequirementsCommand(VirtualEnvCommand):
    command = 'pip'
    extra_args = ['install', '-r']
    file_name = 'requirements.txt'

    def another_file(self, text):
        self.extra_args.append(text)
        super(PipInstallRequirementsCommand, self).run()

    def run(self):
        self.extra_args = ['install', '-r']
        if os.path.exists(self.file_name):
            self.extra_args.append(self.file_name)
            super(PipInstallRequirementsCommand, self).run()
        else:
            sublime.message_dialog('requirements.txt not found')
            self.window.show_input_panel('File to install', self.another_file, None, None)


class SetVirtualEnvCommand(VirtualEnvCommand):

    def is_enabled(self):
        return True

    def find_virtualenvs(self, venv_paths):
        binary = "Scripts" if PLATFORM == 'Windows' else "bin"
        venvs = set()
        for path in venv_paths:
            path = os.path.expanduser(path)
            pattern = os.path.join(path, "*", binary, "activate_this.py")
            venvs.update(list(map(os.path.dirname, glob.glob(pattern))))
        return sorted(venvs)

    def set_virtualenv(self, venvs, index):
        if index == -1:
            return
        name, directory = venvs[index]
        log('Virtual environment "{0}" is set'.format(name))
        binary = os.path.join(directory, 'python')
        self.settings.set("python_bin", binary)
        sublime.save_settings(SETTINGS_FILE)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        choices = self.find_virtualenvs(venv_paths)
        choices = [[path.split(os.path.sep)[-2], path] for path in choices]
        self.choose(choices, self.set_virtualenv)


class ChangeDefaultCommand(VirtualEnvCommand):

    def use_default(self):
        self.settings.erase('python_bin')
        sublime.save_settings(SETTINGS_FILE)

    def run(self):
        self.use_default()


class DjangoClickCommand(sublime_plugin.TextCommand):
    TEMPLATE_DIR = 'templates'

    def parse_tag(self, line):

        RE_PARAMS = re.compile(r'(with)|(\w+=[\'"]\w+[\'"])')

        RE_BLOCK = re.compile(
            r'.*{%%\s*(?P<tag>%s)\s+(?P<names>.+)?[\'"]?\s*%%}'
            % '|'.join(['include', 'extends', 'includeblocks']))
        RE_NAMES = re.compile(r'[\'"]([/\.\-_a-zA-Z0-9\s]+)[\'"]')

        line = re.sub(RE_PARAMS, "", line)

        match = re.match(RE_BLOCK, line)

        if match:
            targets = re.findall(RE_NAMES, match.groupdict()['names'])

            return match.groupdict()['tag'], targets

        return None, []

    def run(self, edit):
        region = self.view.sel()[0]
        line = self.view.line(region)
        line_contents = self.view.substr(line)

        tag, targets = self.parse_tag(line_contents)

        if tag:
            # get the base-path of current file
            base, current_file = self.view.file_name().split(
                '%(separator)stemplates%(separator)s' % dict(
                    separator=os.path.sep), 1)

            for one in targets:
                # get the target file path
                tar = os.path.join(base, self.TEMPLATE_DIR, one)

                # open it!
                window = sublime.active_window()
                window.open_file(tar, sublime.ENCODED_POSITION)


class DjangoBoilerPlate(sublime_plugin.WindowCommand):
    options = ['urls', 'models', 'views', 'admin', 'forms', 'tests']

    def on_done(self, index):
        if index < 0:
            return
        urls = """from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'example.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),
                       )
"""
        admin = """from django.contrib import admin

# Register your models here.
"""
        views = """from django.shortcuts import render
# Create your views here.
"""
        models = """from django.db import models
# Define your models here
"""
        forms = """from django import forms
# Create your forms here
"""
        tests = """from django.test import TestCase

# Create your tests here.
"""
        # actions = OrderedDict((name, eval(name)) for name in self.options)
        actions = OrderedDict()
        for option in self.options:
            actions[option] = eval(option)
        text = actions[self.options[index]]
        self.view = self.window.active_view()
        self.view.run_command('write_helper', {"text": text})

    def run(self):
        self.window.show_quick_panel(self.options, self.on_done)


class WriteHelperCommand(sublime_plugin.TextCommand):

    def run(self, edit, text):
        self.view.insert(edit, 0, text)


class DjangoNewProjectCommand(SetVirtualEnvCommand):

    def folder_selected(self, index):
        self.create_project(directory=self.window.folders()[index])

    def check_folders(self, name):
        if len(self.window.folders()) == 1:
            self.create_project(name=name, directory=self.window.folders()[0])
        else:
            self.name = name
            self.window.show_quick_panel(self.window.folders(), self.folder_selected)

    def create_project(self, **kwargs):
        name = kwargs.get('name')
        directory = kwargs.get('directory')
        if name is not None:
            pass
        else:
            name = self.name
        order = os.path.join(os.path.abspath(os.path.dirname(self.interpreter)), "django-admin.py")
        command = [self.interpreter, order, "startproject", name, directory]
        log(command)
        subprocess.Popen(command)

    def set_interpreter(self, index):
        if index == -1:
            return
        name, self.interpreter = self.choices[index]
        if name is not "default":
            self.interpreter = os.path.join(self.interpreter, 'python')
        self.window.show_input_panel("Project name", "", self.check_folders, None, None)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        version = self.settings.get("python_version")
        envs = self.find_virtualenvs(venv_paths)
        self.choices = [[path.split(os.path.sep)[-2], path] for path in envs]
        self.choices.append(["default", shutil.which(self.interpreter_versions[version])])
        sublime.message_dialog("Select a python interpreter for the new project")
        self.window.show_quick_panel(self.choices, self.set_interpreter)


class DjangoOpenDocsCommand(DjangoCommand):

    def get_version(self):
        binary = self.get_executable()
        command = [binary, '-c', 'import django;print(django.get_version())']
        output = subprocess.check_output(command)
        version = re.match(r'(\d\.\d)', output.decode('utf-8')).group(0)
        if float(version) > LATEST_DJANGO_RELEASE:
            version = 'dev'
        return version

    def run(self):
        version = self.get_version()
        url = "https://docs.djangoproject.com/en/{}/".format(version)
        self.window.run_command('open_url', {'url': url})


class DjangoSearchDocsCommand(DjangoOpenDocsCommand):

    def on_done(self, text):
        releases = {'1.3': 5, '1.4': 6, '1.5': 7, '1.6': 9, '1.7': 11, '1.8': 13, 'dev': 1}
        release = releases[self.get_version()]
        params = {'q': text, 'release': release}
        url = "https://docs.djangoproject.com/search/?{}".format(urlencode(params))
        self.window.run_command('open_url', {'url': url})

    def run(self):
        self.window.show_input_panel('Search:', '', self.on_done, None, None)
