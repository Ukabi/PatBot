from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Message, Embed, TextChannel
from utils.imports import TextChannelConverter, COLOR
from utils.changesettings import change_reference


class Poll(cmd.Cog):
    def __init__(self):
        self.figures = {n: "{}\u20e3".format(n) for n in range(1, 10)}
        self.sep = "|"
        self.config = Cfg.get_conf(self, 668)

        default = {"channel": 0}

        self.config.register_guild(**default)
    
    @cmd.admin()
    @cmd.group(name='poll')
    async def poll_group(self, ctx: cmd.Context):
        pass
    
    @cmd.admin()
    @poll_group.command(name='create')
    async def poll_create(self, ctx: cmd.Context, *, args):
        """**[question] | [proposition] | [proposition] | ... ** : 
        submits a poll to precised channel.
        """
        args = [prop.strip() for prop in args.split(sep=self.sep)]

        if len(args) > 1:
            message = "\n\n".join(
                ["{}: {}".format(
                    self.figures[n + 1], p) for n, p in enumerate(args[1:])
                ]
            )
            
            try:
                channel = ctx.guild.get_channel(
                    await self.config.guild(ctx.guild).channel()
                )
                embed = Embed(
                    title=args[0],
                    color=COLOR,
                    description=message
                )
                message = await channel.send(embed=embed)
                await self.set_first_reactions(message, len(args) - 1)
                embed = Embed(
                    title="Poll sent",
                    color=COLOR,
                    description="Poll sent to <#{}>".format(channel.id)
                )
            
            except:
                embed = Embed(
                    title="Error",
                    color=COLOR,
                    description="Channel removed or not given."
                )
            
        elif len(args) > 9:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="Too many propositions.\n"
                            "Max propositions: 9."
            )

        else:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="Not enough arguments,\n"
                            "it may be an entry error."
            )
        
        await ctx.send(embed=embed)
    
    @cmd.admin()
    @poll_group.command(name='channel')
    async def poll_channel(self, ctx: cmd.Context, channel: str):
        """
        **[#channel or channel name]** : 
        sets the channel where to send polls.
        """
        await change_reference(
            ctx,
            channel,
            self.config.guild(ctx.guild).channel,
            "Channel"
        )

    async def set_first_reactions(self, message: Message, n_prop: int):
        for i in range(1, n_prop + 1):
            await message.add_reaction(self.figures[i])


def setup(bot):
    bot.add_cog(Poll())