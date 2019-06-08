from redbot.core import commands as cmd
from discord import Embed, File
from pathlib import Path
from utils.imports import EmojiConverter, RoleConverter, COLOR
from utils.askconfirm import ask_confirm
import requests as rq
import io

class Emoji(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_path = "{}/emojis/".format(
            Path(__file__).parent.parent.parent.absolute()
        )
    
    @cmd.mod()
    @cmd.group(name='emoji')
    async def emoji_group(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @emoji_group.command(name='add')
    async def emoji_add(self, ctx: cmd.Context, file_path: str, name: str, *roles):
        """
        **[file] [name] (roles)** : adds an emoji to the server,
        if roles, restricts it for precised roles.
        """
        def send_error():
            return Embed(
                title="Error",
                color=COLOR,
                description="File not found."
            )

        roles = [await RoleConverter().convert_(ctx, role) for role in roles]

        if None in roles:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="One of the precised roles wasn't found."
            )

        else:
            affected_roles = ", ".join(
                [str(role) for role in roles]
            ) if roles else "everyone"

            passed = False
            if file_path.startswith("http"):
                req = rq.get(file_path)
                if req.ok:
                    b = bytearray(req.content)
                    f = io.BytesIO(bytes(req.content))
                    passed = True
                else:
                    embed = send_error()
            else:
                try:
                    with open(self.emoji_path + file_path, 'rb') as image:
                        i = image.read()
                        b = bytearray((i))
                        f = io.BytesIO(bytes(i))
                    passed = True
                    
                except FileNotFoundError:
                    embed = send_error()
            
            if passed:
                message = "Confirm emote add?\nReply with y/n."
                
                f = File(f, filename="emoji_template.png")

                answer = await ask_confirm(bot=self.bot, ctx=ctx,
                                           pic=f, conf_mess=message)

                if answer:
                    emoji = await ctx.guild.create_custom_emoji(name=name,
                                                                image=b,
                                                                roles=roles)
                    embed = Embed(
                        title="Successfully created {} emoji.".format(str(emoji)),
                        color=COLOR,
                        description="Affected roles: {}.".format(affected_roles)
                    )
                else:
                    embed = Embed(
                        title="Cancelled",
                        color=COLOR,
                        description="Emote adding process cancelled."
                    )
            else:
                embed = send_error()

        await ctx.send(embed=embed)

    @cmd.admin()
    @emoji_group.command(name='remove')
    async def emoji_remove(self, ctx: cmd.Context, emoji):
        """**[emoji]** : removes emoji from server."""
        emoji = await EmojiConverter().convert_(ctx, emoji)
        
        message = "Affected emoji: {}\nWrite y/n to confirm removal.".format(emoji)
        
        answer = await ask_confirm(bot=self.bot, ctx=ctx, conf_mess=message)

        if answer:
            await emoji.delete()
            embed = Embed(
                title="Reset.",
                color=COLOR,
                description="Emoji removed from server."
            )
        else:
            embed = Embed(
                title="Cancelled",
                color=COLOR,
                description="Removal cancelled."
            )
        
        await ctx.send(embed= embed)
    
    @cmd.mod()
    @emoji_group.command(name='list')
    async def emoji_list(self, ctx: cmd.Context):
        """: shows the server's emoji list."""
        emojis = ctx.guild.emojis

        message = "No emoji." if not emojis else ""

        for emoji in emojis:
            message += "{}".format(emoji)
            if emoji.managed:
                message += " - Twitch"
            elif emoji.roles:
                message += " - Roles: {}".format(
                    ", ".join([str(role) for role in emoji.roles])
                )
            message += "\n"
        
        embed = Embed(
            title="Server's emojis list",
            color=COLOR,
            description=message
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Emoji(bot))