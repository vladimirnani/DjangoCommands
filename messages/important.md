Django manage commands 1.7.9

 - Fallback for 'linux-terminal' setting with a dash is dropped, now is essential to use 'linux_terminal' setting with and underscore.

 - Linux extended compatibility dropping 'gnome-terminal' in favor of 'x-terminal-emulator' as the default 'linux_terminal' setting and with 'xterm' as a fallback.

 - Easier access to user settings and keybindings, now showing both default and user defined files side by side to ease the definition of user settings.

 - Mac OSX users now can select their preferred terminal emulator to be triggered to run the corresponding command. Use `osx_terminal` setting.

 - Windows users, would you like to be able to select another terminal instead of cmd.exe like mintty, cmder or git-bash? If so please open an Issue(only one please so others can comment on it, and keep the issue tracker organized) at our github repo and let us know.

 - Windows slight performance optimization.

 - Minor fixes.