from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Member, Embed
from utils.imports import TextChannelConverter, COLOR


class Welcome(cmd.Cog):
    def __init__(self):
        self.config = Cfg.get_conf(self, 666)
        
        default = {
            "title": "Welcome!",
            "message": "Welcome to the server {0.mention}!",
            "channel": 0
        }

        self.config.register_guild(**default)
    
    @cmd.group(name='welcome')
    async def welcome_group(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @welcome_group.command(name='message')
    async def welcome_message(self, ctx: cmd.Context, *, text):
        """**[text]** : edits the welcome message's text."""
        await self.change_message(
            ctx,
            text,
            self.config.guild(ctx.guild).message
        )
    
    @cmd.admin()
    @welcome_group.command(name='title')
    async def welcome_title(self, ctx: cmd.Context, *, text):
        """**[text]** : edits the welcome message's title."""
        await self.change_message(
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
        channel = await TextChannelConverter().convert_(ctx, channel)

        if channel is None:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="Channel reference not found."
            )
        else:
            await self.config.guild(ctx.guild).channel.set(channel.id)
            embed = Embed(
                title="Channel changed",
                color=COLOR,
                description=str(channel)
            )

        await ctx.send(embed=embed)

    async def change_message(self, ctx: cmd.Context, text, change_type):
        text = text.replace("\\n", "\n")

        try:
            embed = Embed(
                title="Message changed - example:",
                color=COLOR,
                description=text.format(ctx.author)
            )
            await change_type.set(text)

        except AttributeError:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="Wrong attribute."
            )
        except IndexError:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="Wrong format."
            )

        finally:
            await ctx.send(embed=embed)
    
    async def on_member_join(self, member: Member):
        guild = member.guild

        text  = await self.config.guild(guild).message()
        title = await self.config.guild(guild).title()
        channel = member.guild.get_channel(
            await self.config.guild(guild).channel()
        )

        embed = Embed(
            title=title.format(member),
            color=COLOR,
            description=text.format(member)
        )

        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Welcome())