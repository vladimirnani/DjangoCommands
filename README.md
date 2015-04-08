# DjangoCommands for ST3

###The best tool for your django development.

This tool is a Sublime Text wrapper around django `manage.py` commands.

With it you can run django commands like `Django: Run Server`, `Django: Sync Database`, `Django: Migrate` from Command Palette.

You can also run `Django: Custom Command` to access other manage.py commands. Try `Django: Help` and you will get full list of commands provided by each application.

Or you can choose to use `Django: Other Command` to list and run all commands available to `manage.py`

Currently tested on Windows 7/8, Mac OS, Ubuntu.

Everything tested and running!

* __Django 1.7 support__
* __Virtualenv support__
* __Django boilerplate__
* __Install your dependencies__
* __Install new pip packages__
* __Open and search in django documentation from the editor__
* __Create new projects from ST__
* __Start new apps__
* __South support__
* __PostgreSQL specific features snippets__
* __And More!__

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
 * `Django: New Project`
 * `Django: New App`
 * `Django: Run Server`
 * `Django: Boilerplate`
 * `Django: Sync Database`
 * `Django: Test`
 * `Django: Test All`
 * `Django: Shell`
 * `Django: DB Shell`
 * `Django: Custom Command`
 * `Django: Other Command`
 * `Django: Check`
 * `Django: Help`
 * `Django: Open Docs`
 * `Django: Search in Docs`
 * `Django: Use Default Interpreter`
 * `Django: Make Migration`
 * `Django: SQLMigration` 
 * `Django: Migrate Database`
 * `Django: Initial Schema Migration`
 * `Django: Schema Migration`
 * `Django: List Migrations`
 * `Django: Click`

#### Virtual Environment:
 * `Django: Set Virtual Environment`
 * `Django: Terminal Here`
 * `Django: Pip Freeze`
 * `Django: Pip Freeze To File`
 * `Django: Pip Install Packages`
 * `Django: Pip Install Requirements`

### Settings

 * `python_bin`: path to python interpreter
 * `python_version` : default python interpreter version
 * `python_virtualenv_paths`: list of paths where virtualenvs are located (ex:`~/.virtualenvs/`)*
 * `server_host`: host for the runserver command
 * `server_port`: port for the server to listen
 * `linux_terminal`: Only Linux setting for command line emulator
 * `project_override`: (Boolean) Per project setting "python_interpreter" overrides "python_bin"

 __It's important to set your envs directories__

 __Check that your 'linux\_terminal' setting uses an underscore "\_"__

#### Please report any issue, bug, enhacement or comment [here](https://github.com/vladimirnani/DjangoCommands/issues) 
#### We'll be glad to read and work on all of them


