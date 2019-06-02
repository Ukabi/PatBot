from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, Member
from periodic import Periodic
from datetime import datetime as dt
from datetime import timedelta as td
import time
import numpy as np
from utils.imports import TextChannelConverter, COLOR
from utils.changesettings import change_channel

class Birthday(cmd.Cog):
    def __init__(self, bot):
        self.config = Cfg.get_conf(self, 669)
        self.timer = None
        self.bot = bot

        default = {
            "birthdays": list(),
            "channel": 0
        }

        default_global = {
            "date": dt.now().day
        }

        self.config.register_guild(**default)
        self.config.register_global(**default_global)
    
    def __unload(self):
        if self.timer is not None:
            self.timer = None

    @cmd.group(name='birthday')
    async def birthday_group(self, ctx: cmd.Context):
        pass
    
    @cmd.admin()
    @birthday_group.command(name='channel')
    async def birthday_channel(self, ctx: cmd.Context, *, channel: str):
        """**[#channel or channel name]** : 
        sets the channel where to send birthday notifications.
        """
        await change_channel(
            ctx,
            channel,
            self.config.guild(ctx.guild).channel
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

        possible_formats = [
            '%d-%m', '%d.%m', '%d/%m',
            '%d %b', '%d %B', '%dth %b', '%dth %B',
            '%b %d', '%B %d', '%b %dth', '%B %dth'
        ]
        months = [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ]

        passed = False

        for form in possible_formats:
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
                    months[date.tm_mon - 1]
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
    @birthday_group.command(name='show')
    async def birthday_show(self, ctx: cmd.Context):
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
            title='Birthday list',
            color=COLOR,
            description=message
        )

        await ctx.send(embed=embed)

    async def on_member_join(self, member: Member):
        await self.edit_presence(member, True)
    
    async def on_member_leave(self, member: Member):
        await self.edit_presence(member, False)
    
    async def edit_presence(self, member: Member, presence_type: bool):
        birthdays = await self.config.guild(member.guild).birthdays()

        for member in birthdays:
            if member['id'] == member.id:
                member['present'] = presence_type
                await self.config.guild(member.guild).birthdays.set(birthdays)
                break


    @cmd.is_owner()
    @cmd.group(name='scheduler')
    async def scheduler_group(self, ctx: cmd.Context):
        pass
    
    @cmd.is_owner()
    @scheduler_group.command(name='start')
    async def scheduler_start(self, ctx: cmd.Context):
        """ : Starts scheduler. One update every minute."""
        if self.timer is not None:
            embed = Embed(
                title='Error',
                color=COLOR,
                description="Scheduler already started."
            )
        else:
            self.timer = Periodic(60, self.check_day_update)
            await self.timer.start()
            embed = Embed(
                title='Started',
                color=COLOR,
                description="Scheduler started."
            )
        await ctx.send(embed=embed)

    @cmd.is_owner()
    @scheduler_group.command(name='stop')
    async def scheduler_stop(self, ctx: cmd.Context):
        """ : Stops scheduler."""
        if self.timer is None:
            embed = Embed(
                title='Error',
                color=COLOR,
                description="Scheduler not started yet."
            )
        else:
            await self.timer.stop()
            self.timer = None
            embed = Embed(
                title='Stopped',
                color=COLOR,
                description="Scheduler stopped."
            )
        await ctx.send(embed=embed)
    
    async def check_day_update(self):
        d1 = await self.config.date()
        d2 = dt.now().day
        if d1 != d2:
            await self.config.date.set(d2)
            await self.send_birthday_notif()

    async def send_birthday_notif(self):
        guilds = await self.config.all_guilds()

        for guild in guilds.keys():
            guild_data = guilds[guild]

            guild = self.bot.get_guild(guild)

            birthdays = guild_data['birthdays']
            channel = guild.get_channel(guild_data['channel'])


            date = (dt.now().day, dt.now().month)

            birthdays = [
                user['id'] for user in birthdays if user['present']\
                                                    and date == user['date']
            ]
            for user in birthdays:
                user = guild.get_member(user)
                message = ":tada: Happy birthday {.mention}!!! :cake:".format(user)

                await channel.send(message)

def setup(bot):
    bot.add_cog(Birthday(bot))