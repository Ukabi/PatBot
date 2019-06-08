from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, Message, Reaction, Member, Guild, TextChannel
import re
from utils.imports import EmojiConverter, MemberConverter, COLOR, EMOJI_REG, TextChannelConverter
from utils.askconfirm import ask_confirm, ask_reset


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
    
    @cmd.admin()
    @emojidata_group.command(name='gethistory')
    async def emojidata_gethitsory(self, ctx: cmd.Context):
        count = 0
        count_l = list()
        channels = ctx.guild.channels

        embed = Embed(
            title="Count progress",
            color=COLOR,
            description=""
        )

        progress = await ctx.send(embed=embed)

        for channel in channels:
            if isinstance(channel, TextChannel):
                count_c = 0
                async for message in channel.history(limit=100000):
                    count += 1
                    count_c += 1
                    print(count, end=' ')

                    await self.on_message(message)
                    for reaction in message.reactions:
                        async for user in reaction.users():
                            await self.on_reaction_add(reaction, user)

                    if not count % 100:
                        edit = "{}\n{}\n\n{}".format(
                            "\n".join([" - ".join(["{}".format(d) for d in c]) for c in count_l]),
                            "{} process: {}".format(channel, count_c),
                            "Total processed message: {}".format(count)
                        )
                        embed = Embed(
                            title="Count progress",
                            color=COLOR,
                            description=edit
                        )
                        await progress.edit(embed=embed)

                count_l.append((channel, count_c))
        
        message = "{}\n\nTotal processed messages: {}".format(
            "\n".join([" - ".join(c) for c in count_l]),
            count
        )

        embed = Embed(
            title="History tracking result",
            color=COLOR,
            description=message
        )
    
        await ctx.send(embed=embed)
        

    @emojidata_group.group(name='guild')
    async def emojidata_group_guild(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @emojidata_group_guild.command(name='enable')
    async def emojidata_guild_enable(self, ctx: cmd.Context):
        """: enables guild data collection."""
        await self.config.guild(ctx.guild).enabled_guild.set(True)

    @cmd.admin()
    @emojidata_group_guild.command(name='disable')
    async def emojidata_guild_disable(self, ctx: cmd.Context):
        """: disables guild data collection."""
        await self.config.guild(ctx.guild).enabled_guild.set(False)

    @emojidata_group_guild.command(name='show')
    async def emojidata_guild_show(self, ctx: cmd.Context, top=10):
        data = await self.config.guild(ctx.guild).data()
        await self.make_data(
            ctx,
            data,
            int(top),
            "Emoji stats for {.name}".format(ctx.guild)
        )

    @cmd.admin()    
    @emojidata_group_guild.command(name='reset')
    async def emojidata_group_reset(self, ctx: cmd.Context):
        """: resets the emoji data list."""
        await ask_reset(
            bot=self.bot,
            ctx=ctx,
            res_func=self.config.guild(ctx.guild).data.clear,
            obj="Guild emoji data list",
            message="Write y/n to confirm reset"
        )

    @emojidata_group.group(name='user')
    async def emojidata_group_user(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @emojidata_group_user.command(name='enable')
    async def emojidata_user_enable(self, ctx: cmd.Context):
        """: enables member data collection."""
        await self.config.guild(ctx.guild).enabled_members.set(True)

    @cmd.admin()
    @emojidata_group_user.command(name='disable')
    async def emojidata_user_disable(self, ctx: cmd.Context):
        """: disables member data collection."""
        await self.config.guild(ctx.guild).enabled_members.set(False)

    @emojidata_group_user.command(name='show')
    async def emojidata_user_show(self, ctx: cmd.Context, *args):
        """**(member) (top)** : shows member emoji data."""
        passed_top = False
        passed_member = False

        top = 10
        member = ctx.author

        for n, arg in enumerate(args):
            if n > 1:
                break
            else:
                try:
                    if not passed_top:
                        top = int(arg)
                        passed_top = True
                    else:
                        int('bleh')
                except ValueError:
                    if not passed_member:
                        temp_member = await MemberConverter().convert_(ctx, arg)
                        if temp_member is not None:
                            passed_member = True
                            member = temp_member

        data = await self.config.member(member).data()
        await self.make_data(
            ctx,
            data,
            top,
            "Emoji stats for {.name}".format(member)
        )

    @cmd.admin()
    @emojidata_group_user.command(name='reset')
    async def emojidata_user_reset(self, ctx: cmd.Context):
        """: resets the emoji data list."""
        await ask_reset(
            bot=self.bot,
            ctx=ctx,
            res_func=self.config.clear_all_members,
            args=(ctx.guild),
            obj="Member emoji data list",
            message="Write y/n to confirm reset"
        )
    
    async def make_data(self, ctx: cmd.Context, data: dict, top: int, title: str):
        top = 25 if top > 25 else top

        data = list(data.items())
        data.sort(key=lambda x: x[1], reverse=True)

        m = "" if data else "No emoji data."
        for e, c in data[:top]:
            temp = await EmojiConverter().convert_(ctx, e)

            if isinstance(temp, str) or temp is None:
                pass
            elif not temp.managed:
                e = temp
            else:
                e = temp.name

            m += "{} - {}\n".format(e, c)

        embed = Embed(
            title=title,
            color=COLOR,
            description=m
        )

        await ctx.send(embed=embed)
    
    @cmd.Cog.listener()
    async def on_message_without_command(self, message: Message):
        print(1)
        content = message.content

        emotes = self.reg_cut.findall(content)
        emojis = [[f for f in e if f][0] for e in EMOJI_REG.findall(content)]

        keys = [self.reg_key.search(e).group(0) for e in emotes] + emojis
        print(keys)

        await self.add_emoji_to_data(
            message.guild,
            message.author,
            keys
        )

    @cmd.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, member: Member):
        emoji = reaction.emoji

        if not isinstance(emoji, str):
            emoji = emoji.name

        try:
            await self.add_emoji_to_data(
                member.guild,
                member,
                [emoji]
            )
        except:
            pass
    
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


def setup(bot):
    bot.add_cog(EmojiData(bot))