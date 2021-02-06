#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from discord import Intents
from discord.ext import commands
from .json_db import JsonDB


def get_prefix(bot, message):
    if not message.guild:
        return bot.default_prefix

    prefixes = [bot.prefixes.get(message.guild.id, bot.default_prefix)]
    personal_prefix = bot.prefixes.get(message.author.id)
    if personal_prefix is not None:
        prefixes.append(personal_prefix)
    return prefixes


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        self.default_prefix = 'a'
        self.log = logging.getLogger(self.__class__.__name__)
        self.ttt_games = set()
        kwargs['intents'] = Intents(messages=True, reactions=True, guilds=True)
        super().__init__(get_prefix, **kwargs)

        self.loop.create_task(self.load_cogs())             # fucking use json because setting up
        self.prefixes = JsonDB('prefixes', loop=self.loop)  # db takes fucking time
        self.exps = JsonDB('exps', loop=self.loop)

    @property
    def raw_cogs(self):
        return [f'cogs.{i[:-3]}'
                for i in os.listdir('cogs')
                if i.endswith('.py')]

    async def load_cogs(self):
        await self.wait_until_ready()
        for cog in self.raw_cogs:
            try:
                self.load_extension(cog)
                self.log.info('%s has been loaded', cog)
            except Exception as e:
                self.log.error('Failed to load %s', cog, exc_info=e)

    async def on_ready(self):
        self.log.info('Logged in as %s', self.user)
