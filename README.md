# DjangoCommands for ST2/ST3

This tool is a Sublime Text wrapper around django manage.py commands. 

With it you can run django commands like runserver, syncdb, migrate from Command Palette.
You can also run Django: Custom Command to access other manage.py commands.


Currently only tested on Windows 7

## Installation

### Package Control

The easiest way to install this is with [Package Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text before doing this next bit.
 * Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select `Django Manage Commands` when the list appears.

Package Control will automatically keep plugin up to date with the latest version.

## Use

### Commands
Currently supports following commands:
 * Django: Run Server
 * Django: Sync Database
 * Django: Migrate
 * Django: Custom Command

### Settings

 * `python_bin`: path to python interpreter
 * `manage_py`: path to manage.py file
 * `python_virtualenv_paths`: list of path where virtualenvs are located 

