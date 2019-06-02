from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Member, Embed
from utils.imports import TextChannelConverter, COLOR
from utils.changesettings import change_data, change_channel


class Welcome(cmd.Cog):
    def __init__(self):
        self.config = Cfg.get_conf(self, 666)
        
        default = {
            "title": "Welcome!",
            "message": "Welcome to the server {0.mention}!",
            "channel": 0
        }

        self.config.register_guild(**default)
    
    @cmd.admin()
    @cmd.group(name='welcome')
    async def welcome_group(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @welcome_group.command(name='message')
    async def welcome_message(self, ctx: cmd.Context, *, text):
        """**[text]** : edits the welcome message's text."""
        await change_data(
            ctx,
            text,
            self.config.guild(ctx.guild).message
        )
    
    @cmd.admin()
    @welcome_group.command(name='title')
    async def welcome_title(self, ctx: cmd.Context, *, text):
        """**[text]** : edits the welcome message's title."""
        await change_data(
            ctx,
            text,
            self.config.guild(ctx.guild).title
        )

    @cmd.admin()
    @welcome_group.command(name='channel')
    async def welcome_channel(self, ctx: cmd.Context, channel):
        """**[#channel or channel name]** : 
        sets the channel where to send messages.
        """
        await change_channel(
            ctx,
            channel,
            self.config.guild(ctx.guild).channel
        )
    
    async def on_member_join(self, member: Member):
        guild = member.guild

        text  = await self.config.guild(guild).message()
        title = await self.config.guild(guild).title()
        channel = await self.config.guild(guild).channel()
        channel = member.guild.get_channel(channel)

        embed = Embed(
            title=title.format(member),
            color=COLOR,
            description=text.format(member)
        )

        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcome())