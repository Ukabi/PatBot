from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, Member
from discord.ext import tasks
from periodic import Periodic
from datetime import datetime as dt
from datetime import timedelta as td
import time
import numpy as np
from utils.imports import TextChannelConverter, MemberConverter
from utils.imports import COLOR, MONTHS, DATE_FORMATS
from utils.changesettings import change_reference

class Birthday(cmd.Cog):
    def __init__(self, bot):
        self.config = Cfg.get_conf(self, 669)
        self.bot = bot

        self.scheduler.start()
        print("BIRTHDAY_COG: Scheduler started.")

        default = {
            "birthdays": list(),
            "channel": 0,
            "role": 0
        }

        default_global = {
            "date": dt.now().day
        }

        self.config.register_guild(**default)
        self.config.register_global(**default_global)
    
    def cog_unload(self):
        self.scheduler.cancel()
        print("BIRTHDAY_COG: Scheduler stopped.")
    
    @tasks.loop(minutes=1)
    async def scheduler(self):

        d1 = await self.config.date()
        d2 = dt.now().day
        if d1 != d2:
            print("BIRTHDAY_COG: New day !")
            await self.config.date.set(d2)
            await self.update_birthday()

    @scheduler.before_loop
    async def before_scheduler(self):
        await self.bot.wait_until_ready()

    async def update_birthday(self):
        guilds = await self.config.all_guilds()

        for guild in guilds.keys():
            guild_data = guilds[guild]

            guild = self.bot.get_guild(guild)

            birthdays = guild_data['birthdays']
            channel = guild.get_channel(guild_data['channel'])
            role = guild.get_role(guild_data['role'])

            date = (dt.now().day, dt.now().month)

            birthdays = [
                user['id'] for user in birthdays if user['present']\
                                                    and date == user['date']
            ]
            for user in birthdays:
                user = guild.get_member(user)
                message = ":tada: Happy birthday {.mention}!!! :cake:".format(user)

                #await channel.send(message)
            
            if role:
                for member in guild.members:
                    roles = member.roles
                    if member.id in birthdays and role not in roles:
                        await member.add_roles(role)
                    elif member.id not in birthdays and role in roles:
                        await member.remove_roles(role)

    @cmd.group(name='birthday')
    async def birthday_group(self, ctx: cmd.Context):
        pass
    
    @cmd.admin()
    @birthday_group.command(name='channel')
    async def birthday_channel(self, ctx: cmd.Context, *, channel: str):
        """**[#channel or channel name]** : 
        sets the channel where to send birthday notifications.
        """
        await change_reference(
            ctx,
            channel,
            self.config.guild(ctx.guild).channel,
            "Channel"
        )

    @cmd.admin()
    @birthday_group.command(name='role')
    async def birthday_role(self, ctx: cmd.Context, *, role: str):
        """**[@role or role name]** : 
        sets the role to give during birthday.
        """
        await change_reference(
            ctx,
            role,
            self.config.guild(ctx.guild).role,
            "Role"
        )
    
    @birthday_group.command(name='set')
    async def birthday_set(self, ctx: cmd.Context, *, date: str):
        """**[date]** : Sets birthday date. Will send a server notification
         on the precised day.
         Possible formats: `dd/mm`, `dd.mm`, `d month`, `month d`.
        """
        def send_error():
            return Embed(
                title='Error',
                color=COLOR,
                description="Couldn't format argument.\n"
                            "Possible formats: "
                            "`dd/mm`, `dd.mm`, `d month`, `month d`."
            )

        passed = False

        for form in DATE_FORMATS:
            try:
                date = time.strptime(date, form)
                if date:
                    passed = True
                    break
            except ValueError:
                pass
            except:
                embed = send_error()
        
        if not passed:
            embed = send_error()
        
        else:
            birthdays = await self.config.guild(ctx.guild).birthdays()
            date_ = (date.tm_mday, date.tm_mon)

            member = {
                'id': ctx.author.id,
                'date': tuple(date_),
                'present': True
            }

            try:
                index = [member['id'] for member in birthdays].index(ctx.author.id)
                birthdays[index] = member
            except ValueError:
                birthdays.append(member)
            except:
                embed = send_error()
            
            to_sort = [list(member['date']) for member in birthdays]
            to_sort = [list(date) for date in zip(*to_sort)]
            order = np.lexsort(to_sort)
            birthdays = [birthdays[i] for i in order]

            await self.config.guild(ctx.guild).birthdays.set(birthdays)

            embed = Embed(
                title='Birthday set!',
                color=COLOR,
                description='Birthday set to {} {}'.format(
                    date.tm_mday,
                    MONTHS[date.tm_mon - 1]
                )
            )

        await ctx.send(embed=embed)
    
    @birthday_group.command(name='remove')
    async def birthday_remove(self, ctx: cmd.Context):
        """ : Removes date from birthdays list."""
        birthdays = await self.config.guild(ctx.guild).birthdays()

        index = [member['id'] for member in birthdays].index(ctx.author.id)
        del birthdays[index]

        await self.config.guild(ctx.guild).birthdays.set(birthdays)

        embed = Embed(
            title='Birthday removed',
            color=COLOR,
            description='Birthday remove from list.'
        )

        await ctx.send(embed=embed)
    
    @cmd.admin()
    @birthday_group.command(name='list')
    async def birthday_list(self, ctx: cmd.Context):
        """ : Shows birthdays list."""
        bdays = await self.config.guild(ctx.guild).birthdays()

        bdays = [
            (
                "{.name}".format(ctx.guild.get_member(user.pop('id'))),
                "/".join([str(d) for d in user.pop('date')]),
                ["❌", "✅"][user.pop('present')]
            ) for user in bdays
        ]

        message = "\n".join([" - ".join(info) for info in bdays])

        embed = Embed(
            title='Birthdays list',
            color=COLOR,
            description=message
        )

        await ctx.send(embed=embed)

    @cmd.Cog.listener()
    async def on_member_join(self, member: Member):
        await self.edit_presence(member, True)
    
    @cmd.Cog.listener()
    async def on_member_leave(self, member: Member):
        await self.edit_presence(member, False)
    
    async def edit_presence(self, member: Member, presence_type: bool):
        birthdays = await self.config.guild(member.guild).birthdays()

        for member in birthdays:
            if member['id'] == member.id:
                member['present'] = presence_type
                await self.config.guild(member.guild).birthdays.set(birthdays)
                break

def setup(bot):
    bot.add_cog(Birthday(bot))