import sublime
import sublime_plugin
import threading
import subprocess
import os
import glob
import re

from ntpath import basename as ntbasename, split as ntsplit
from shutil import which
from platform import system
from functools import partial
from collections import OrderedDict
from urllib.parse import urlencode

SETTINGS_FILE = 'DjangoCommands.sublime-settings'
PLATFORM = system()
TERMINAL = ''


def log(message):
    print(' - Django: {0}'.format(message))


class DjangoCommand(sublime_plugin.WindowCommand):
    project_true = True
    error = False
    error_msg = None

    def __init__(self, *args, **kwargs):
        self.settings = sublime.load_settings(SETTINGS_FILE)
        self.interpreter_versions = {2: "python2",
                                     3: "python3"} if PLATFORM is not "Windows" else {2: "python", 3: "python"}
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)

    @property
    def startupinfo(self):
        if PLATFORM == 'Windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            return startupinfo
        else:
            return None

    def get_executable(self):
        self.project_true = self.settings.get('project_override')
        settings_interpreter = self.settings.get('python_bin')
        project = self.window.project_data()
        settings_exists = 'settings' in project.keys()
        if settings_exists and self.project_true:
            project_interpreter = project['settings'].get('python_interpreter')
            if project_interpreter is not None and self.project_true is True:
                return project_interpreter
            elif project_interpreter is not None and self.project_true is False:
                return settings_interpreter
            else:
                version = self.settings.get("python_version")
                return which(self.interpreter_versions[version])
        elif settings_interpreter is not None:
            return settings_interpreter
        else:
            version = self.settings.get("python_version")
            return which(self.interpreter_versions[version])

    def get_version(self, extb=None):
        if extb is None:
            binary = self.get_executable()
        else:
            binary = extb
        command = [binary, '-c', 'import django;print(django.get_version())']

        try:
            output = subprocess.check_output(command, startupinfo=self.startupinfo)
        except subprocess.CalledProcessError:
            self.error = True
            self.error_msg = "No django module was found, check if Django is installed in the current environment"
            return 0
        else:
            version = re.match(r'(\d\.\d+)', output.decode('utf-8')).group(0)
            return version

    def find_manage_py(self):
        django_project_root = \
            sublime.active_window().active_view().settings().get('django_project_root') \
            or self.settings.get('django_project_root')
        print(django_project_root)
        for path in [django_project_root] if django_project_root else sublime.active_window().folders():
            for root, dirs, files in os.walk(path):
                if 'manage.py' in files:
                    return os.path.join(root, 'manage.py')
                else:
                    self.error = True
                    self.error_msg = "manage.py not found, unable to proceed"
                    return None

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
        if(os.path.exists(base_dir)):
            os.chdir(base_dir)
        else:
            self.error = True
            self.error_msg = "Project root not found"
            return

    def format_command(self, command):
        binary = self.get_executable()
        self.manage_py = self.find_manage_py()
        self.go_to_project_home()

        command = [binary, self.manage_py] + command.split(' ')
        return command

    def define_terminal(self):
        global TERMINAL
        if PLATFORM == "Linux":
            TERMINAL = self.settings.get('linux_terminal')
            if TERMINAL is None:
                TERMINAL = self.settings.get(
                    'linux-terminal', 'gnome-terminal')

    def display_error_message(self):
        sublime.error_message(self.error_msg)
        self.error = False

    def display_process_error_message(self, process):
        outs, err = process.communicate()
        if err and err.decode():
            sublime.error_message(err.decode())
        else:
            return

    def run_command(self, command):
        self.define_terminal()
        commands = self.format_command(command)
        if self.error:
            self.display_error_message()
            return
        thread = CommandThread(commands)
        thread.start()


class CommandThread(threading.Thread):

    def __init__(self, command, cwd='.', notsplit=False):
        self.command = command
        self.notsplit = notsplit
        self.cwd = cwd
        threading.Thread.__init__(self)

    def run(self):
        env = os.environ.copy()

        if PLATFORM == 'Windows':
            command = ['cmd.exe', '/k', self.command[0], '{}'.format(self.command[1])]
            for index, param in enumerate(self.command):
                if(index < 2):
                    continue
                else:
                    if param:
                        command.append(param)
            command.extend(['&&', 'timeout', '/T', '10', '&&', 'exit'])

        elif(self.notsplit):
            command = "{}".format(' '.join(self.command))

        else:
            command = "{}".format(' '.join([cmd.replace(' ', "\ ") for cmd in self.command]))

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
        try:
            subprocess.Popen(command, env=env, cwd=self.cwd)
        except (subprocess.CalledProcessError, ValueError, OSError) as e:
            sublime.message_dialog("{}".format(e))


class DjangoSimpleCommand(DjangoCommand):
    command = ''
    extra_args = []

    def get_command(self):
        return "{} {}".format(self.command, " ".join(self.extra_args))

    def run(self):
        self.extra_args = []
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
        self.manage_py = self.find_manage_py()
        base_dir = os.path.dirname(self.manage_py)
        choices = [self.prettify(path, base_dir) for path in choices]
        self.choose(choices, self.on_choose_app)


class DjangoOtherCommand(DjangoSimpleCommand):

    def get_commands(self):
        command = self.format_command('help --commands')
        out = str(subprocess.check_output(command, startupinfo=self.startupinfo))
        out = re.search('b\'(.*)\'', out).group(1)
        commands = out.split(
            '\\n')[:-1] if PLATFORM is not "Windows" else out.split('\\r\\n')[:-1]
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
        port = self.settings.get('server_port', "8000")
        host = self.settings.get('server_host', "127.0.0.1")
        self.extra_args = [host, port]
        inComannd = "{} {}:{}".format(self.command, host, port)
        self.run_command(inComannd)


class DjangoRunCustomCommand(DjangoSimpleCommand):

    def get_script(self, executable, script_name):
        return os.path.join(os.path.dirname(executable), script_name)

    def run(self):
        project = self.window.project_data()
        p_settings = 'settings' in project.keys()
        self.custom_command = project['settings'].get('server_custom_command') if p_settings else None
        self.define_terminal()
        executable = self.get_executable()
        script = self.custom_command.get('command')
        script = script if os.path.exists(script) else self.get_script(executable, script)
        commands = [executable, script, " ".join(self.custom_command.get('args'))] if self.custom_command.get(
            'run_with_python', True) else ["", script, " ".join(self.custom_command.get('args'))]
        thread = CommandThread("{} {} {}".format(*commands), cwd=os.path.dirname(self.find_manage_py()))
        if self.error:
            self.display_error_message()
            return
        else:
            thread.start()


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

    def path_leaf(self, path):
        head, tail = ntsplit(path)
        return os.path.splitext(tail)[0] or os.path.splitext(ntbasename(head))[0]

    def is_enabled(self):
        return True

    def on_choose_migration(self, apps, index):
        if index == -1:
            return
        self.extra_args.append(apps[index])
        self.run_command(
            "{} {} {}".format(self.command, self.name, " ".join(self.extra_args)))

    def on_app_selected(self, apps, index):
        self.name = apps[index]
        path = os.path.join(
            os.path.dirname(self.find_apps()[index]), 'migrations')
        migrations = [_path for _path in map(self.path_leaf, glob.iglob(os.path.join(path, r'*.py')))]
        migrations.remove('__init__')
        sublime.set_timeout(
            lambda: self.choose(migrations, self.on_choose_migration), 20)

    def run(self):
        self.extra_args = []
        self.go_to_project_home()
        choices = self.find_apps()
        self.manage_py = self.find_manage_py()
        base_dir = os.path.dirname(self.manage_py)
        choices = [self.prettify(path, base_dir) for path in choices]
        self.choose(choices, self.on_app_selected)


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

    def find_virtualenvs(self, venv_paths):
        binary = "Scripts" if PLATFORM == 'Windows' else "bin"
        venvs = set()
        for path in venv_paths:
            path = os.path.expanduser(path)
            pattern = os.path.join(path, "*", binary, "activate_this.py")
            venvs.update(list(map(os.path.dirname, glob.glob(pattern))))
        return sorted(venvs)

    def run(self):
        self.define_terminal()
        self.manage_py = self.find_manage_py()
        self.go_to_project_home()
        bin_dir = os.path.dirname(self.settings.get('python_bin'))
        command = [os.path.join(bin_dir, self.command)] + self.extra_args
        thread = CommandThread(command)
        thread.start()


class TerminalHereCommand(VirtualEnvCommand):
    command = 'activate'

    def run(self):
        self.define_terminal()
        self.manage_py = self.find_manage_py()
        self.go_to_project_home()
        bin_dir = os.path.dirname(self.settings.get('python_bin'))
        if PLATFORM == 'Windows':
            command = ['cmd', '/k', '{}'.format(os.path.join(bin_dir, self.command))]
        if PLATFORM == 'Linux' or PLATFORM == 'Darwin':
            command = ["bash", "--rcfile", "<(echo '. ~/.bashrc && . {}')".format(os.path.join(bin_dir, self.command))]
        thread = CommandThread(command, notsplit=True)
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


class PipInstallPackagesCommand(VirtualEnvCommand):
    command = 'pip'
    extra_args = ['install']

    def appendPackages(self, text):
        self.extra_args.append(text)
        super(PipInstallPackagesCommand, self).run()

    def run(self):
        self.extra_args = ['install']
        self.window.show_input_panel(
            'Packages', '', self.appendPackages, None, None)


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
            self.window.show_input_panel(
                'File to install', '', self.another_file, None, None)


class SetVirtualEnvCommand(VirtualEnvCommand):

    def is_enabled(self):
        return True

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


class SetProjectInterpreterCommand(VirtualEnvCommand):

    def is_enabled(self):
        return True

    def set_project_interpreter(self, venvs, index):
        if index == -1:
            return
        project = self.window.project_data()
        if "settings" in project.keys():
            pass
        else:
            project["settings"] = {}
        project["settings"]["python_interpreter"] = os.path.join(venvs[index][1], 'python')
        self.window.set_project_data(project)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        choices = self.find_virtualenvs(venv_paths)
        choices = [[path.split(os.path.sep)[-2], path] for path in choices]
        self.choose(choices, self.set_project_interpreter)


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
            base, current_file = self.view.file_name().split(
                '%(separator)stemplates%(separator)s' % dict(
                    separator=os.path.sep), 1)

            for one in targets:
                tar = os.path.join(base, self.TEMPLATE_DIR, one)
                if os.path.isfile(tar):
                    window = sublime.active_window()
                    window.open_file(tar, sublime.ENCODED_POSITION)
                else:
                    for root, dirs, filenames in os.walk(base):
                        for f in filenames:
                            if f == one:
                                tar = os.path.join(root, one)
                                window = sublime.active_window()
                                if os.path.exists(tar):
                                    window.open_file(
                                        tar, sublime.ENCODED_POSITION)


class DjangoBoilerPlate(sublime_plugin.WindowCommand):
    options = ['urls', 'models', 'views', 'admin', 'forms', 'tests']

    def on_done(self, index):
        if index < 0:
            return
        urls = """from django.conf.urls import patterns, include, url

urlpatterns = [
                       # Examples:
                       # url(r'^$', 'example.views.home', name='home'),
                       # url(r'^blog/', include(blog.urls)),
                       ]
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
        actions = OrderedDict()
        for option in self.options:
            actions[option] = eval(option)
        text = actions[self.options[index]]
        self.view = self.window.active_view()
        self.view.run_command('write_helper', {"text": text, "point": 0})

    def run(self):
        self.window.show_quick_panel(self.options, self.on_done)


class WriteHelperCommand(sublime_plugin.TextCommand):

    def run(self, edit, point, text):
        self.view.insert(edit, point, text)


class DjangoNewProjectCommand(SetVirtualEnvCommand):

    def folder_selected(self, index):
        self.create_project(directory=self.window.folders()[index])

    def check_folders(self, name):
        if len(self.window.folders()) == 1:
            self.create_project(name=name, directory=self.window.folders()[0])
        else:
            self.name = name
            self.window.show_quick_panel(
                self.window.folders(), self.folder_selected)

    def create_project(self, **kwargs):
        name = kwargs.get('name')
        directory = kwargs.get('directory')
        if name is not None:
            pass
        else:
            name = self.name
        order = os.path.join(
            os.path.abspath(os.path.dirname(self.interpreter)), "django-admin.py")
        command = [self.interpreter, order, "startproject", name, directory]
        log(command)
        process = subprocess.Popen(command, startupinfo=self.startupinfo)
        self.display_process_error_message(process)

    def set_interpreter(self, index):
        if index == -1:
            return
        name, self.interpreter = self.choices[index]
        if name is not "default":
            self.interpreter = os.path.join(self.interpreter, 'python')
        if self.get_version(self.interpreter) == 0:
            self.error_msg = "No module 'django' found in the selected environment"
            self.display_error_message()
            return
        self.window.show_input_panel(
            "Project name", "", self.check_folders, None, None)

    def run(self):
        venv_paths = self.settings.get("python_virtualenv_paths", [])
        version = self.settings.get("python_version")
        envs = self.find_virtualenvs(venv_paths)
        self.choices = [[path.split(os.path.sep)[-2], path] for path in envs]
        self.choices.append(
            ["default", which(self.interpreter_versions[version])])
        sublime.message_dialog(
            "Select a python interpreter for the new project")
        self.window.show_quick_panel(self.choices, self.set_interpreter)


class DjangoNewAppCommand(DjangoSimpleCommand):
    command = 'startapp'

    def create_app(self, text):
        self.extra_args.append(text)
        command = self.format_command(self.get_command())
        log(command)
        if self.error:
            self.display_error_message()
        else:
            process = subprocess.Popen(command, env=os.environ.copy(), stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE, startupinfo=self.startupinfo)
            self.display_process_error_message(process)

    def run(self):
        if self.get_version() == 0:
            self.display_error_message()
            return
        self.extra_args = list()
        self.window.show_input_panel(
            "App name", '', self.create_app, None, None)


class DjangoOpenDocsCommand(DjangoCommand):

    def run(self):
        version = self.get_version()
        if version == 0:
            self.display_error_message()
            return
        url = "https://docs.djangoproject.com/en/{}/".format(version)
        self.window.run_command('open_url', {'url': url})


class DjangoSearchDocsCommand(DjangoCommand):

    def on_done(self, text):
        release = self.get_version()
        if release == 0:
            self.display_error_message()
            return
        params = {'q': text}
        url = "https://docs.djangoproject.com/en/{}/search/?{}".format(
            release,
            urlencode(params))
        self.window.run_command('open_url', {'url': url})

    def run(self):
        sel = self.window.active_view().substr(self.window.active_view().sel()[0])
        if(sel is not None):
            selection = sel
        else:
            selection = ''
        self.window.show_input_panel('Search:', selection, self.on_done, None, None)
