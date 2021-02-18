#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Norizon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import json
import logging

from core.bot import Bot

with open("config.json", "r") as f:
    config = json.load(f)


log = logging.getLogger("")
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s " "[%(module)s]:%(lineno)d %(message)s"
)

ch.setFormatter(formatter)
log.addHandler(ch)


bot = Bot()
bot.run(config["token"])
