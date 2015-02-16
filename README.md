# DjangoCommands for ST2/ST3

###The best tool for your django development chores.

This tool is a Sublime Text wrapper around django `manage.py` commands.

With it you can run django commands like `Django: Run Server`, `Django: Sync Database`, `Django: Migrate` from Command Palette.

You can also run `Django: Custom Command` to access other manage.py commands. Try `Django: Help` and you will get full list of commands provided by each application.


Currently tested on Windows 7/8, Mac OS, Ubuntu.

Everything tested and running!

* __Django 1.7 support__
* __Virtualenv support__
* __django boilerplate__
* __create new projects from ST__
* __South support__


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

### Settings

 * `python_bin`: path to python interpreter
 * `python_version` : default python interpreter version
 * `python_virtualenv_paths`: list of paths where virtualenvs are located (ex:`~/.virtualenvs/`)*
 * `server_host`: host for the runserver command
 * `server_port`: port for the server to listen
 * `linux_terminal: Only Linux setting for command line emulator`
*_it's important to set your envs directories_ *



##Django Click

With the [Django Click](https://sublime.wbond.net/packages/Django%20Click) plugin no longer in active development, I tried to fix the issues, and after consulting with the repository owner, the functionalities and fixes have been implemented inside "Django Manage Commands" with the command:

* `Django: Click`

and all the known keybindings and everything.

People only using "Django click" still can use it as it will be mantained by a contributor of "Django Manage Commands" [Proyecto513](https://github.com/Proyecto513)

Thanks to [Kahi](https://github.com/kahi) for this useful tool.

#### Please report any issue, bug, enhacement or comment [here](https://github.com/vladimirnani/DjangoCommands/issues) 
#### I'll be glad to read your feedbacks


