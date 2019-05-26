<h1 align="center">
  <br>
  Patter-Cogs
  <br>
</h1>

# Overview

Patter-Cogs is an cog pack extension of the original [Red-DiscordBot project](https://github.com/Cog-Creators/Red-DiscordBot), which is a fully modular Discord bot. It provides some basic or utility independant modules which can be useful in any Discord server.

# Requirements

Those libraries are needed to make cogs working correctly (installable via pip):
- [Red-DiscordBot](https://red-discordbot.readthedocs.io/en/v3-develop/install_windows.html#installing-red)
- discord
- asyncio-periodic

# Installation

- See the different [installation guides](https://red-discordbot.readthedocs.io/en/v3-develop/index.html) provided by the Red team.
- Insert the [utils](https://github.com/Ukabi/Patter-Cogs/tree/master/venv/lib/python3.7/site-packages/utils) function pack into your Python libraries path.
- Insert the [cogs](https://github.com/Ukabi/Patter-Cogs/tree/master/RedBot/cogs/CogManager/cogs) into the cogs path (/cogs/CogManager/cogs by default).
- Enable cogs using the [p]load command on Discord.

# Cogs

The current cogs provided are:
- Welcome: send a custom welcome message to new member.
- Poll: Create a multiple choice poll using Discord reactions.
- Emoji: Import - role-restricted - emojis.
- Rolegive: Give members roles when reacting to a message.
- Birthday: Members can give their birthday therefore guild will be notified.

# Support

- Using the [p]cog command, it will show cog help pannel.