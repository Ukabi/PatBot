<h1 align="center">
  <br>
  Patter-Cogs
  <br>
</h1>

# Overview

Patter-Cogs is a cog pack extension of the original [Red-DiscordBot project](https://github.com/Cog-Creators/Red-DiscordBot), which is a fully modular Discord bot.
It provides some basic or utility independant modules which can be useful in any Discord server.

# Requirements

Those libraries are needed to make cogs working correctly (installable via pip):
- [Red-DiscordBot](https://red-discordbot.readthedocs.io/en/v3-develop/install_windows.html#installing-red)
- discord.py 1.1.1
- asyncio-periodic

# Installation

- See the different [installation guides](https://red-discordbot.readthedocs.io/en/v3-develop/index.html) provided by the Red team.
- Insert the [utils](https://github.com/Ukabi/Patter-Cogs/tree/master/venv/lib/python3.7/site-packages/utils) function pack into your Python libraries path.
- Insert the [cogs](https://github.com/Ukabi/Patter-Cogs/tree/master/RedBot/cogs/CogManager/cogs) into the cogs path (/cogs/CogManager/cogs by default).
- Enable cogs using the [p]load command on Discord.

# Cogs

The current cogs provided are:
- Birthday: Members can give their birthday therefore guild will be notified.
- Emoji: Import - role-restricted - emojis.
- EmojiData: Gets the emoji usage and provides statistics for guild or member. 
- Poll: Create a multiple choice poll using Discord reactions.
- Rolegive: Give members roles when reacting to a message.
- Scheduler: Reminds user the task they submited after a certain amount of time.
- Welcome: Send a custom welcome message to new member.

# Support

- Using the [p]cog command, it will show cog help pannel.