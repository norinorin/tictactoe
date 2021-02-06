#!/usr/bin/env python
# -*- coding: utf-8 -*-
from discord.ext import commands


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Shows the WebSocket latency
        """
        latency = round(self.bot.latency * 1000, 2)
        await ctx.send(f'WebSocket heartbeat: {latency}')

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx, *, prefix=None):
        if not prefix:
            if not ctx.guild:
                return await ctx.send(f'Prefix is {self.bot.default_prefix}')

            prefix = self.bot.prefixes.get(ctx.guild.id, self.bot.default_prefix)
            return await ctx.send(f'Prefix for this guild is {prefix}')

        warn = False
        if len(prefix) >= 20:
            warn = True
            prefix = prefix[:20]

        await self.bot.prefixes.put(ctx.guild.id, prefix)
        return await ctx.send(f'Guild prefix has been set to {prefix}'
                              f'\n{"Note that prefix can only have 20 chars max"*warn}')

    @prefix.command()
    async def user(self, ctx, *, prefix=None):
        if not prefix:
            prefix = self.bot.prefixes.get(ctx.author.id)
            if prefix is None:  # explicit is better than implicit
                await ctx.send('You don\'t have personal prefix yet!')
            else:
                await ctx.send(f'Your personal prefix is {prefix}')

        warn = False
        if len(prefix) >= 20:
            warn = True
            prefix = prefix[:20]

        await self.bot.prefixes.put(ctx.author.id, prefix)
        return await ctx.send(f'Personal prefix has been set to {prefix}'
                              f'\n{"Note that prefix can only have 20 chars max"*warn}')


def setup(bot): bot.add_cog(Meta(bot))
