# What #

A single-server IRC bot with a semi-modular script plug-in system.

It comes with these functions configured by default:

- `!help [command]`
  - Prints out help messages to the channel about what scripts there are
- `!insult`
  - Prints a shakespearean insult
- `!w [-s <save_zipcode>] [query_zipcode]`
  - Prints information about the weather at zip code
  - Will attempt to geolocate user if no zip code is specified
  - Allows tying a zipcode to user via the -s switch
- `!fortune [category]`
  - Prints a short fortune, optionally of a specified category
- `!8ball [question]`
  - Prints a random magic 8-ball reply
- `!remind [-s|m|-h|-d] <time> <message>`
  - Schedule a message to be announced after a certain time
  - -s, -m, -h, or -d specifies the time to be in seconds, minutes, hours, or
    days
- `!replace [-l <line> | -s] <pattern> <replacement>`
  - Replace pattern in a user's previous message with replacement
  - Sort of like sed. In fact, it can also be triggered by
    s/<pattern>/<replacement>
  - The -l or --line option allows you specify which line to replace
  - The -s option tells replace to search backwards and edit the most
    recent line in which the pattern matches something
- `!choose [options...]`
  - Will choose for you

If you call its nickname in a public message, it will respond with a markov
chain generated reply.

Clearly very useful stuff, especially the insult.

# Install #

You must first install the package with:

    python setup.py install

If you don't have root privileges to install Python packages, then installing
it within a virtualenv environment also works fine. After this is done, you
must generate a config file for fortunebot by running:

    fortunebot-generate-config

This will create a config directory (probably in ~/.config/fortunebot) and copy
the default config file into it. All of the settings under Connect must be
present, but the ones under Scripts are not critical. Any missing settings for
a particular script will simply prevent that script from loading.

Finally, to run the bot, simply invoke:

    fortunebot

Use the `--help` flag to see a full list of options.

# Dependencies #

The bot is tested with Python 2.7 and 3.4 on a Debian-based system.
