#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import asyncio
import json
import os
import uuid


class JsonDB:
    def __init__(self, name, *, loop=None):
        self.name = f"{name}.json"
        self.loop = loop or asyncio.get_event_loop()
        self.lock = asyncio.Lock()
        self.initialize()

    def initialize(self):
        try:
            with open(self.name, "r") as f:
                self._db = json.load(f)

        except FileNotFoundError:
            self._db = {}

    def __contains__(self, item):
        return self.db.__contains__(str(item))

    def __getitem__(self, item):
        return self.db.__getitem__(str(item))

    def __len__(self):
        return self.db.__len__()

    @property
    def db(self):
        return self._db

    async def remove(self, key):
        del self.db[str(key)]
        await self.save()

    async def put(self, key, value):
        self.db[str(key)] = value
        await self.save()

    def get(self, key, *args):
        return self.db.get(str(key), *args)

    def _dump(self):
        temp = "%s-%s.tmp" % (uuid.uuid4(), self.name)
        with open(temp, "w", encoding="utf-8") as tmp:
            json.dump(self.db.copy(), tmp, ensure_ascii=True, separators=(",", ":"))

        # replace the json
        os.replace(temp, self.name)

    async def save(self):
        async with self.lock:
            await self.loop.run_in_executor(None, self._dump)
