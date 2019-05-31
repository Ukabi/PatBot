from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, Message, Reaction, Member, Guild
import re
from utils.imports import EmojiConverter, MemberConverter, COLOR, EMOJI_REG
from utils.askconfirm import ask_confirm


class EmojiData(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Cfg.get_conf(self, 670)

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
        
        self.reg_cut = re.compile("<:[\w~]+:[0-9]+>")
        self.reg_key = re.compile("(?<=:)[\w~]+(?=:)")

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
        await self.make_data(ctx, data, "Emoji stats for guild")
    
    @emojidata_group_guild.command(name='reset')
    async def emojidata_group_reset(self, ctx: cmd.Context):
        """: resets the emoji data list."""
        message = "Write y/n to confirm reset."

        answer = await ask_confirm(bot=self.bot, ctx=ctx, conf_mess=message)

        if answer:
            await self.config.guild(ctx.guild).data.clear()
            embed = Embed(
                title="Reset.",
                color=COLOR,
                description="Guild emoji data list has been reset."
            )
        else:
            embed = Embed(
                title="Cancelled",
                color=COLOR,
                description="Reset cancelled."
            )
        
        await ctx.send(embed=embed)

    @emojidata_group.group(name='user')
    async def emojidata_group_user(self, ctx: cmd.Context):
        pass

    @emojidata_group_user.command(name='enable')
    async def emojidata_user_enable(self, ctx: cmd.Context):
        await self.config.guild(ctx.guild).enabled_members.set(True)

    @emojidata_group_user.command(name='disable')
    async def emojidata_user_disable(self, ctx: cmd.Context):
        await self.config.guild(ctx.guild).enabled_members.set(False)
    
    @emojidata_group_user.command(name='show')
    async def emojidata_user_show(self, ctx: cmd.Context, *member):
        if not member:
            member = ctx.author
        else:
            member = await MemberConverter().convert_(ctx, member[0])
        
        if member is None:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="User not found."
            )
        else:
            data = await self.config.member(member).data()
            await self.make_data(ctx, data, "Emoji stats for {.mention}".format(member))
    
    @emojidata_group_user.command(name='reset')
    async def emojidata_user_reset(self, ctx: cmd.Context):
        """: resets the emoji data list."""
        message = "Write y/n to confirm reset."

        answer = await ask_confirm(bot=self.bot, ctx=ctx, conf_mess=message)

        if answer:
            await self.config.clear_all_members(ctx.guild)
            embed = Embed(
                title="Reset.",
                color=COLOR,
                description="Member emoji data list has been reset."
            )
        else:
            embed = Embed(
                title="Cancelled",
                color=COLOR,
                description="Reset cancelled."
            )
        
        await ctx.send(embed=embed)
    
    async def make_data(self, ctx: cmd.Context, data: dict, title: str):
        data = list(data.items())
        data.sort(key=lambda x: x[1], reverse=True)
        m = ""
        for e, c in data[:10]:
            temp = await EmojiConverter().convert_(ctx, e)
            if isinstance(temp, str) or temp is None:
                pass
            elif not temp.managed:
                e = temp
            m += "{} - {}\n".format(e, c)
        await ctx.send(m)
    
    async def on_message(self, message: Message):
        content = message.content
        emotes = self.reg_cut.findall(content)
        emojis = [[f for f in e if f][0] for e in EMOJI_REG.findall(content)]
        keys = [self.reg_key.search(e).group(0) for e in emotes] + emojis
        await self.add_emoji_to_data(
            message.guild,
            message.author,
            keys
        )

    async def on_reaction_add(self, reaction: Reaction, member: Member):
        emoji = str(reaction.emoji)
        emoji = emoji if len(emoji) == 1 else emoji[1:-1]
        await self.add_emoji_to_data(
            member.guild,
            member,
            [emoji]
        )
    
    async def add_emoji_to_data(self, guild: Guild, member: Member, keys: list):
        guild_conf = self.config.guild(guild)
        member_conf = self.config.member(member)
        treat = [
            [None, await guild_conf.data()][await guild_conf.enabled_guild()],
            [None, await member_conf.data()][await guild_conf.enabled_members()]
        ]
        
        for n, val in enumerate(treat):
            if val is not None:
                for key in keys:
                    count = val.get(key, 0) + 1
                    val[key] = count
                await [guild_conf, member_conf][n].data.set(val)
    
    @cmd.command(name="test")
    async def a_test(self, ctx: cmd.Context, m):
        temp = await EmojiConverter().convert_(ctx, m)
        await self.make_data(ctx, await self.config.member(ctx.author).data(), "")
        await ctx.send(m)
        await ctx.send("{}".format(temp))
        d = await self.config.member(ctx.author).data()
        m = list()
        for e, c in d.items():
            temp = await EmojiConverter().convert_(ctx, e)
            e = e if temp is None else temp
            await ctx.send("{}".format(e))
    
    @cmd.command(name="test1")
    async def b_test(self, ctx: cmd.Context, *, m):
        await ctx.send(m)


def setup(bot):
    bot.add_cog(EmojiData(bot))