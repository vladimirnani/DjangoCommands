import sublime, sublime_plugin
import threading
import sys,os,re
import subprocess

def read_settings():
    settings = sublime.load_settings("DjangoCommands.sublime-settings")
    python_bin = settings.get('python_bin')
    manage_py = settings.get('manage_py_path')
    return (python_bin,
            manage_py)

class DjangoRunCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = read_settings()
        if not settings:
            return
        thread = DjangoThread('runserver', *settings)
        thread.start()

class DjangoSyncdbCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = read_settings()
        if not settings:
            return
        thread = DjangoThread('syncdb', *settings)
        thread.start()

class DjangoMigrateCommand(sublime_plugin.WindowCommand):
    def run(self):
        settings = read_settings()
        if not settings:
            return
        thread = DjangoThread('migrate', *settings)
        thread.start()

class DjangoThread(threading.Thread):

    def __init__(self, action, python, manage_py):
        self.python = python
        self.manage_py = manage_py
        self.action = action
        threading.Thread.__init__(self)


    def speak_output(self, lines, errlines):

        if len(errlines) > 2 and "raise" in errlines[-3]:
            sublime.error_message("Fatal pylint error:\n%s" % (errlines[-2]))

        for line in lines:           
            print line

    def run(self):                
        command = [self.python, self.manage_py, self.action]
        print command
        
        if not self.action =='runserver':
            p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
            output, eoutput = p.communicate()
           
            lines = [line for line in output.split('\n')]  
            elines = [line for line in eoutput.split('\n')]
        
            sublime.set_timeout(lambda: self.speak_output(lines, elines), 500)
        else:
            p = subprocess.Popen(command)