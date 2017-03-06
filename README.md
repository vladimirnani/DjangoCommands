<a href="https://packagecontrol.io/packages/Django%20Manage%20Commands"><img src="https://packagecontrol.herokuapp.com/downloads/Django%20Manage%20Commands.svg?color=42A672"></a>

     ____  _                           __  __                                           
    |  _ \(_) __ _ _ __   __ _  ___   |  \/  | __ _ _ __   __ _  __ _  ___              
    | | | | |/ _` | '_ \ / _` |/ _ \  | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \             
    | |_| | | (_| | | | | (_| | (_) | | |  | | (_| | | | | (_| | (_| |  __/             
    |____// |\__,_|_| |_|\__, |\___/  |_|  |_|\__,_|_| |_|\__,_|\__, |\___|             
        |__/             |___/                                  |___/                   
      ____                                          _                                   
     / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___                               
    | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|                              
    | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \                              
     \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/                              
                                                                                        
#########################################################################################

## Django manage commands

### The best tool for your django development.

## Overview

This tool is a Sublime Text wrapper around django `manage.py` commands.

### So you can create new `Django` projects and apps directly from Sublime text like this

![new project](http://i.giphy.com/3oKIPjMXcl4xWh4Y8M.gif "New project screen")

### Make migrations, migrate the database  or run tests

![migrations](http://i.giphy.com/3oKIPnnN6HjE0ofhde.gif "make migrations")

### And run the test server
![runserver](http://i.giphy.com/3oKIPdSCp3XDX7Eqze.gif "run server")  

### Even run tests

![Tests](http://i.giphy.com/3oKIPfFrzQvmUj50Ji.gif "tests")  


You can also run `Django: Custom Command` to access other manage.py commands. Try `Django: Help` and you will get full list of commands provided by each application.

Or you can choose to use `Django: Other Command` to list and run all commands available to `manage.py`

![other](http://i.giphy.com/3oKIPAwltfeuKESVTW.gif "other commands")  

Currently tested on Windows 7/8/10, Mac OS, Ubuntu and many other linux distros.

Everything tested and running!

* __Virtualenv support__
* __Django boilerplate__
* __Install your dependencies__
* __Install new pip packages__
* __Open and search in django documentation from the editor__
* __Run custom servers__
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
 * `Django: Run Custom Server`
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
 * `Django: Set Project Interpreter`

### Settings

 * `python_bin`: path to python interpreter
 * `python_version` : default python interpreter version
 * `python_virtualenv_paths`: list of paths where virtualenvs are located (ex:`~/.virtualenvs/`)\* 
 * `server_host`: host for the runserver command
 * `server_port`: port for the server to listen
 * `linux_terminal`: Linux only setting for command line emulator\*\*
 * `project_override`: (Boolean) Per project setting "python_interpreter" overrides "python_bin"
 
 * `server_custom_command`: Per project setting to specify a custom server to run (ex: {"command": "gunicorn", "args":["--workers=3"]})\*\*\* 
 
***

\*It's important to set your envs directories

\*The folders in this list should be the parent folder of the virtualenv folder, not the virtualenv folder itself

\*\*Check that your 'linux\_terminal' setting uses an underscore "\_"

\*\*Default is `x-terminal-emulator` with a fallback to `xterm`

\*\*\*use any script you want

### Please report any issue, bug, enhacement or comment [here](https://github.com/vladimirnani/DjangoCommands/issues) 
### We'll be glad to read and work on all of them


