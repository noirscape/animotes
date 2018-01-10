## animoteBot

A Discord Bot/Cog to use animated emotes, even if you don't have Nitro!

This bot takes advantage of the fact that Discord bots technically have access to all Discord Nitro features except for animated profile pictures.

## Disclaimer
_If I receive any request by Discord to take down this cog, I will. Consider this cog to be fully **unsupported**_. As far as I am aware, this is not against the TOS, but use at your own risk.

## Installation

If you have an existing bot, put the `animotes.py` file in your cogs/plugins folder and use `bot.load_extension(<cogfolder>.animotes)` in the on_ready() call. This might vary slightly depending on your bot/loader used.

After that, you and your users can opt in with the `register` command. Opting out just means running the `register` command again. For ease of use, the `register` command has an alias callded `unregister`

If you want to use the bot framework, download the repository and edit config.yaml to include your token and the prefix at the token line.

## Limitations

- This also works on multiple servers (creating a fake global emote system), since the bot checks for _all_ the emotes it has access to, rather than the ones in the current Guild/server.
- Only works if the bot can "see" the emote. If the bot isnt in a server that contains the animated emote, it won't do anything.
- No wumboji.

## License

GPLv3
