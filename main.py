#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
from core.bot import Bot


with open('config.json', 'r') as f:
    config = json.load(f)


log = logging.getLogger("")
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)s "
                              "[%(module)s]:%(lineno)d %(message)s")

ch.setFormatter(formatter)
log.addHandler(ch)


bot = Bot()
bot.run(config['token'])
