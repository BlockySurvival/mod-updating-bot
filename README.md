# Mod updating bot for Blocky Survival

## Configuration

The bot can be configured by using the variables at the top of the file.

### Example configuration for Discord

```py
CHANNELS = ('#480390668875726850', '#642816690354257960')
DISALLOWED = ('lurklite#1029',)
TOKEN = '(Discord token)'
CRASH_LOGS_DIR = '/path/to/logs/directory'

irc = miniirc_discord.Discord(TOKEN, auto_connect=False, stateless_mode=True)
```

### Example configuration for Matrix

Make sure that the import statement at the top of the file has `miniirc_matrix`
and not `miniirc_discord`.


```py
CHANNELS = ('#server-staff:example.com', '#server:example.com')
DISALLOWED = ('@baduser:example.com',)
HOMESERVER = 'matrix.example.com'
TOKEN = '(Discord token)'
CRASH_LOGS_DIR = '/path/to/logs/directory'

irc = miniirc_matrix.Matrix('matrix.example.com', token=TOKEN,
                            auto_connect=False)
```

Warning: The bot will expect to already be joined to the specified channels
and won't attempt to join them itself.

It's probably possible to connect the bot to IRC as well, however this bot,
along with most IRC clients and servers, don't support multi-line messages.

## Important

The bot's working directory must be the same directory as
`update-bls-mods.sh`, don't run the bot from a directory which other users can
write to as this could allow them to run code as your user.

## Commands

None of these commands require a prefix.

 - `Do the thing`: Runs the `update-bls-mods.sh` script in the current working
    directory.
 - `Give me crash logs`: Show the most recent crash logs.
 - `Give me crash log [n]`: Show the *n*th most recent crash log.

## Log file format

This bot expects that logs are stored as `MMDD.txt` files. Any other file
naming scheme will likely break. I have made an attempt to handle wraparounds
properly, however I may have missed something.
