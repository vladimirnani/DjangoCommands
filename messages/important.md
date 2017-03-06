Django manage commands 1.7.3

 - Fallback for 'linux-terminal' setting with a dash is dropped, now is essential to use 'linux_terminal' setting with and underscore.

 - Linux extended compatibility dropping 'gnome-terminal' in favor of 'x-terminal-emulator' as the default 'linux_terminal' setting and with 'xterm' as a fallback.

 - Easier access to user settings and keybindings, now showing both default and user defined files side by side to ease the definition of user settings.

 - Mac OSX users now can select their preferred terminal emulator to visualize command output, run python/django shell, etc. triggered from Django manage commands.

 - Windows users now can choose among other options of terminals, beside classic cmd prompt, like 'powershell' and 'git bash' and definitively would add support for other emulators, please feel free to sugest one.

 - Minor fixes and performance optimizations.
