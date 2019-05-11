from redbot.core import commands as cmd
from discord import Embed
from pathlib import Path
from utils.imports import EmojiConverter, RoleConverter, COLOR

class Emoji(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_path = "{}/emojis/".format(
            Path(__file__).parent.parent.parent.absolute()
        )
    
    @cmd.group(name='emoji')
    async def emoji_group(self, ctx: cmd.Context):
        pass

    @cmd.admin()
    @emoji_group.command(name='add')
    async def emoji_add(self, ctx: cmd.Context, name: str, file_path: str, *roles):
        """
        **[name] [file] [roles]** : adds an emoji to the server,
        if roles, restricts it for precised roles.
        """
        roles = [await RoleConverter().convert_(ctx, role) for role in roles]

        if None in roles:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="One of the precised roles wasn't found."
            )
        else:
            try:
                with open(self.emoji_path + file_path, 'rb') as image:
                    b = bytearray(image.read())
                
                emoji = await ctx.guild.create_custom_emoji(name=name,
                                                            image=b,
                                                            roles=roles)
                
                affected_roles = ", ".join(
                    [str(role) for role in roles]
                ) if roles else "everyone"

                embed = Embed(
                    title="Successfully created {} emoji.".format(str(emoji)),
                    color=COLOR,
                    description="Affected roles: {}.".format(affected_roles)
                )
                
            except FileNotFoundError:
                embed = Embed(
                    title="Error",
                    color=COLOR,
                    description="Wrong file given."
                )
        
        await ctx.send(embed=embed)
    
    @cmd.admin()
    @emoji_group.command(name='remove')
    async def emoji_remove(self, ctx: cmd.Context, emoji):
        """**[emoji]** : removes emoji from server."""
        emoji = await EmojiConverter().convert_(ctx, emoji)
        
        embed = Embed(
            title="Confirm?",
            color=COLOR,
            description="Affected emoji: {}\n"
                        "Write y/n to confirm removal.".format(emoji)
        )

        await ctx.send(embed=embed)

        def check(m):
            if m.channel != ctx.channel or m.author != ctx.message.author:
                return False
            elif m.content.lower()[0] not in "yn":
                return False
            else:
                return True
        
        confirm = await self.bot.wait_for('message', check=check)

        if confirm.content.lower().startswith("y"):
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