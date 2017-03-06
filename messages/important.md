Django manage commands 1.7.3

 - Fallback for 'linux-terminal' setting with a dash is dropped, now is essential to use 'linux_terminal' setting with and underscore.

 - Linux extended compatibility dropping 'gnome-terminal' in favor of 'x-terminal-emulator' as the default 'linux_terminal' setting and with 'xterm' as a fallback.

 - Mac OSX users now can select their preferred terminal emulator to visualize command output, run python/django shell, etc; And define their own way to open said terminal through AppleScript(osascript).

 - Windows users now can choose among other options of terminals, beside classic cmd prompt, like 'powershell' and 'git bash' and definitively would add support for other emulators, please feel free to sugest one.

 - Minor fixes and performance optimizations.
