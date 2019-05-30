from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, Message, Reaction, Member, Guild
import re
from utils.imports import EmojiConverter, RoleConverter, COLOR, ask_confirm, EMOJI_REG, MemberConverter


class EmojiData(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Cfg(self, 670)

        default = {
            'data': dict(),
            'enabled_guild': False,
            'enabled_members': False
        }

        default_member = {
            'data': dict()
        }

        self.config.register_guild(**default)
        self.config.register_member(**default_member)
        
        self.reg_cut = re.compile("<:\w~]+:[0-9]+>")
        self.reg_key = re.compile("(?<=<:)[\w~")

    @cmd.group(name='emojidata')
    async def emojidata_group(self, ctx: cmd.Context):
        pass

    @emojidata_group.group(name='guild')
    async def emojidata_group_guild(self, ctx: cmd.Context):
        pass

    @emojidata_group_guild.command(name='enable')
    async def emojidata_guild_enable(self, ctx: cmd.Context):
        await self.config.guild(ctx.guild).enabled_guild.set(True)

    @emojidata_group_guild.command(name='disable')
    async def emojidata_guild_disable(self, ctx: cmd.Context):
        await self.config.guild(ctx.guild).enabled_guild.set(False)
    
    @emojidata_group_guild.command(name='show')
    async def emojidata_guild_show(self, ctx: cmd.Context):
        data = await self.config.guild(ctx.guild).data()
        await make_data(ctx, data, "Emoji stats for guild")

    @emojidata_group.group(name='user')
    async def emojidata_group_user(self, ctx: cmd.Context):
        pass

    @emojidata_group_user.command(name='enable')
    async def emojidata_user_enable(self, ctx: cmd.Context):
        await self.config.member(ctx.author).enabled_member.set(True)

    @emojidata_group_user.command(name='disable')
    async def emojidata_user_disable(self, ctx: cmd.Context):
        await self.config.member(ctx.author).enabled_member.set(False)
    
    @emojidata_group_user.command(name='show')
    async def emojidata_user_show(self, ctx: cmd.Context, *member):
        if not member:
            member = ctx.author
        else:
            member = MemberConverter(ctx, member[0])
        
        if member is None:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="User not found."
            )
        else:
            data = await self.config.member(member).data()
            await make_data(ctx, data, "Emoji stats for {.mention}".format(member))
    
    @emojidata_group.command(name='reset')
    async def emojidata_reset(self, ctx: cmd.Conext):
        """: resets the emoji data list."""
        message = "Write y/n to confirm reset."

        answer = await ask_confirm(bot=self.bot, ctx=ctx, conf_mess=message)

        if answer:
            await self.config.guild(ctx.guild).data.set(list())
            embed = Embed(
                title="Reset.",
                color=COLOR,
                description="Emoji data list has been reset."
            )
        else:
            embed = Embed(
                title="Cancelled",
                color=COLOR,
                description="Reset cancelled."
            )
        
        await ctx.send(embed=embed)
    
    async def make_data(self, ctx: cmd.Context, data: dict, title: str):
        datas = data.items()
        message = "\n".join(
            [" - ".join(data) for data in datas]
        )
        pass
    
    async def on_message(self, message: Message):
        emotes = self.reg_cut.findall(message)
        emojis = EMOJI_REG.findall(message)
        keys = [self.reg_key.sub(emote) for emote in emotes] + emojis
        await self.add_emoji_to_data(
            message.guild,
            message.author,
            keys
        )

    async def on_reaction_add(self, reaction: Reaction, member: Member):
        await self.add_emoji_to_data(
            member.guild,
            member,
            [
                str(reaction.emoji)
            ]
        )
    
    async def add_emoji_to_data(self, guild: Guild, member: Member, keys: list):
        guild_conf = await self.config.guild(guild)
        member_conf = await self.config.member(member)

        treat = [
            [None, guild_conf.data()][await guild_conf.enabled_guild()],
            [None, member_conf.data()][await guild_conf.enabled_member()]
        ]
        
        for n, val in enumerate(treat):
            if val is not None:
                for key in keys:
                    count = val.get(key, 0) + 1
                    val[key] = count
                await [guild_conf, member_conf][n].data.set(val)