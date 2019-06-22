from redbot.core import commands as cmd
from redbot.core import Config as Cfg
from discord import Embed, User
from discord.ext import tasks
import re
from datetime import timedelta as td
from datetime import datetime as dt
import time
from utils.imports import COLOR
from utils.askconfirm import ask_confirm


class Scheduler(cmd.Cog):
    def __init__(self, bot):
        self.config = Cfg.get_conf(self, 675)
        self.bot = bot
        
        self.scheduler_loop.start()
        print("SCHEDULER_COG: Scheduler started.")
        
        default = {'tasks': list()}

        self.config.register_user(**default)

        self.reg = re.compile("((\d+)d)?((\d+)h)?((\d+)m)?((\d+)s)?")
    
    def cog_unload(self):
        self.scheduler_loop.cancel()
        print("SCHEDULER_COG: Scheduler stopped.")

    def sec_to_time(self, s):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return d, h, m, s

    @cmd.group(name='scheduler')
    async def scheduler_group(self, ctx: cmd.Context):
        pass
    
    @scheduler_group.command(name='add')
    async def scheduler_add(self, ctx: cmd.Context, delay: str, *args):
        try:
            count = int(args[0])
            args = args[1:]
        except ValueError:
            count = 1
        
        task = " ".join(args)
        task = task[:200]

        if not task:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="No task defined."
            )

        else:
            req = self.reg.search(delay).groups()
            req = [r for n, r in enumerate(req) if n % 2]

            delay = list()
            for n, r in enumerate(req):
                r = 0 if r is None else int(r)
                delay.append(r)
            
            delay = {
                ['days', 'hours', 'minutes', 'seconds'][n]:
                r for n, r in enumerate(delay)
            }

            delta = td(**delay)

            if delta.total_seconds() < 5:
                embed = Embed(
                    title="Error",
                    color=COLOR,
                    description="Delay not undrstood or less than 5 seconds."
                )

            else:
                tasks = await self.config.user(ctx.author).tasks()

                tasks.insert(
                    0,

                    {
                        'count': count,
                        'delay': int(delta.total_seconds()),
                        'date': int(time.time()),
                        'task': task
                    }
                )

                await self.config.user(ctx.author).tasks.set(tasks)

                d = ", ".join(
                    ["{} {}".format(v, t) for t, v in delay.items() if v]
                )

                desc = "Task name: {}\nCount: {}\nDelay: {}".format(
                    task, count, d
                )

                embed = Embed(
                    title="New task set",
                    color=COLOR,
                    description=desc
                )

        await ctx.send(embed=embed)

    @scheduler_group.command(name='remove')
    async def scheduler_remove(self, ctx: cmd.Context, task_number: int):
        tasks = await self.config.user(ctx.author).tasks()
        if task_number in range(1, len(tasks) + 1):
            task = tasks[task_number - 1]['task']

            answer = await ask_confirm(
                ctx=ctx,
                bot=self.bot,
                conf_mess="Task selected: {}\nReply with y/n.".format(task)
            )
            
            if answer:
                del tasks[task_number - 1]

                await self.config.user(ctx.author).tasks.set(tasks)

                embed = Embed(
                    title="Removed",
                    color=COLOR,
                    description="Task removed."
                )
            else:
                embed = Embed(
                    title="Cancelled",
                    color=COLOR,
                    description="Removal cancelled."
                )

        elif not tasks:
            embed = Embed(
                title="Error",
                color=COLOR,
                description="No task stored."
            )
        
        else:
            embed = Embed(
                title='Error',
                color=COLOR,
                description="Wrong task number given."
            )

        await ctx.send(embed=embed)

    @scheduler_group.command(name='list')
    async def scheduler_list(self, ctx: cmd.Context):
        tasks = await self.config.user(ctx.author).tasks()

        if not tasks:
            message = "No task stored."
        else:
            message = str()

        for n, task in enumerate(tasks):
            m = "**{} - {}**: in ".format(n + 1, task['task'])

            next = self.sec_to_time(task['date'] + task['delay'] - int(time.time()))
            next = ["{}{}".format(t, 'dhms'[n]) for n, t in enumerate(next)]
            next = "".join(next)

            m += next

            if task['count'] > 1:
                delay = self.sec_to_time(task['delay'])
                delay = ["{}{}".format(t, 'dhms'[n]) for n, t in enumerate(delay)]
                delay = "".join(delay)

                m += ", looping {} times, {} interval".format(task['count'], delay)

            message += "{}\n".format(m)

        embed = Embed(
            title="Tasks list",
            color=COLOR,
            description=message
        )

        await ctx.send(embed=embed)

    @tasks.loop(seconds=1)
    async def scheduler_loop(self):
        user_tasks = await self.config.all_users()
        for user, tasks in user_tasks.items():
            tasks = tasks['tasks']
            to_treat = list()
            for n, task in enumerate(tasks):
                if task['delay'] + task['date'] < time.time():
                    user = self.bot.get_user(int(user))

                    await self.send_notif(user, task)
                    to_treat.append(n)
            if to_treat:
                await self.treat_tasks(user, to_treat)
    
    @scheduler_loop.before_loop
    async def before_scheduler_loop(self):
        await self.bot.wait_until_ready()
    
    async def send_notif(self, user: User, task: dict):
        channel = user.dm_channel

        if task['count'] == 1:
            count = ""

            next = ""
            
            done = "Done!"

        else:
            count = "Looping for another {} times\n".format(task['count'] - 1)

            next = self.sec_to_time(task['delay'])
            next = ["{}{}".format(t, 'dhms'[n]) for n, t in enumerate(next)]
            next = "".join(next)
            next = "Next: {}\n".format(next)

            done = ""

        message = "Task: {}\n{}{}{}".format(task['task'], count, next, done)

        embed = Embed(
            title="Timer elapsed!",
            color=COLOR,
            description=message
        )

        await channel.send(embed=embed)
    
    async def treat_tasks(self, user: User, treat: list):
        tasks = await self.config.user(user).tasks()

        to_remove = list()
        for n in treat:
            task = tasks[n]
            task['count'] -= 1
            if task['count'] < 1:
                to_remove.append(n)
            else:
                task['date'] += task['delay']

        to_remove.reverse()
        for n in to_remove:
            del tasks[n]
        
        await self.config.user(user).tasks.set(tasks)

def setup(bot):
    bot.add_cog(Scheduler(bot))