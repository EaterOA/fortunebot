# What #

An IRC bot written for the UCLA Linux User Group, #lug@irc.gimp.net. 

Accepts these commands:
- !insult - Insults you elegantly
- !fortune - Outputs a short UNIX fortune cookie
- !8ball - Gives a magic 8-ball response
- !weather - Provides weather information about a specified zipcode
- !remind - Allows users to set reminders for themselves
- !replace - Allows users to correct their most recent message

If you call its nickname in a public message, it will respond with a markov
chain generated reply

Very useful stuff, especially the insult.

# Install #

If you're a sysadmin who wants to install this bot as a daemon on a Debian
system, simply run the install script in the root git directory. This will
create a fortunebot user, init script in /etc/init.d, and standard directories
at /var/run/fortunebot, /var/log/fortunebot, and /var/lib/fortunebot. You can
control the bot with /etc/init.d/fortunebot start, stop, reload, and restart.

You must also configure fortunebot by renaming
/var/lib/fortunebot/fortunebot.conf.example to fortunebot.conf, and editing
whatever settings you want inside. Any missing settings will default to the
same configuration in the example, EXCEPT for server and channel, which must be
read from the config file.

If you don't have admin privileges, unfortunately you still need to find some
way to install the fortunebot python package. virtualenv works great. After you
install the package, you can run the bot by directly invoking botrunner.py.

The above comments about configuration applies here, except you can specify the
location of the config file via command line in botrunner.py. Check
botrunner.py --help to see full list of options.

# Dependencies #

The bot is tested with Python 2.7. Some effort was done to make it future-proof
for Python 3, but it probably doesn't work right out of the box.

The bot uses Python irclib. Find that at http://python-irclib.sourceforge.net/

