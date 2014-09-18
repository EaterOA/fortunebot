# What #

A single-server IRC bot with a semi-modular script plug-in system.

It comes with these functions configured by default:

- !help [command]
  - Prints out help messages to the channel about what scripts there are
- !insult
  - Prints a shakespearean insult
- !w <zip code>
  - Prints information about the weather at zip code
  - Zip code defaults to 90024 (Los Angeles)
- !fortune [category]
  - Prints a short fortune, optionally of a specified category
- !8ball [question]
  - Prints a random magic 8-ball reply
- !remind [-s|m|-h|-d] <time> <message>
  - Schedule a message to be announced after a certain time
  - -s, -m, -h, or -d specifies the time to be in seconds, minutes, hours, or
    days
- !replace [-l <line> | -s] <pattern> <replacement>
  - Replace pattern in a user's previous message with replacement
  - Sort of like sed. In fact, it can also be triggered by
    s/<pattern>/<replacement>
  - The -l or --line option allows you specify which line to replace
  - The -s option tells replace to search backwards and edit the most
    recent line in which the pattern matches something

If you call its nickname in a public message, it will respond with a markov
chain generated reply.

Clearly very useful stuff, especially the insult.

# Install #

If you're a sysadmin who wants to install this bot as a daemon on a Debian
system, simply run the install script in the root git directory. This will
create a fortunebot user, init script in /etc/init.d, and standard directories
at /var/run/fortunebot, /var/log/fortunebot, and /var/lib/fortunebot. You can
control the bot with /etc/init.d/fortunebot start, stop, reload, and restart.

You must also configure fortunebot by renaming
/var/lib/fortunebot/fortunebot.conf.example to fortunebot.conf, and editing
whatever settings you want inside. All settings under Connect must be present,
but the Script settings are not critical. Any missing settings for a particular
script will simply prevent that script from loading.

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

