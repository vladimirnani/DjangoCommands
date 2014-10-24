# DjangoCommands for ST3

This tool is a Sublime Text wrapper around django `manage.py` commands.

With it you can run django commands like `Django: Run Server`, `Django: Sync Database`, `Django: Migrate` from Command Palette.

You can also run `Django: Custom Command` to access other manage.py commands. Try `Django: Help` and you will get full list of commands provided by each application.


Currently tested on Windows 7/8, Mac OS, Ubuntu.

## New Features:

 * Django 1.7 support
 * Option for project interpreter

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

#### Django:

 * `Django: Run Server`
 * `Django: Sync Database`
 * `Django: Test`
 * `Django: Test All`
 * `Django: Shell`
 * `Django: Custom Command`
 * `Django: Check`
 * `Django: Help`
 * `Django: Use Default Interpreter`
 
##### new in Django 1.7
 * `Django: SQLMigration`

###### _(south compatible)_

 * `Django: Migrate Database`
 * `Django: Schema Migration`
 * `Django: List Migrations`

### Settings

 * `python_bin`: path to python interpreter
 * `python_version` : default python interpreter version
 * `python_virtualenv_paths`: list of paths where virtualenvs are located (ex:`~/.virtualenvs/`)

**(it's important to set your envs directories)**

#### Virtual Environment:
 * `Django: Set Virtual Environment`
 * `Django: Terminal Here`
 * `Django: Pip Freeze`

#### Please report any issue, bug, enhacement or comment [here](https://github.com/vladimirnani/DjangoCommands/issues) 
#### I'll be glad to read your feedbacks