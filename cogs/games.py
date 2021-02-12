#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Norizon
Copyright (c) 2017 Clederson Cruz

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
import secrets
from asyncio import TimeoutError
from discord import Member, Embed
from discord.ext import commands


def clamp(val, min_, max_):
    return max(min_, min(max_, val))


class TicTacToe:
    """
    Minimax class implementation
    """

    HUMAN = -1
    COMP = 1

    def __init__(self, ctx, member):
        ctx.bot.ttt_games.add(ctx.channel.id)
        self.ctx = ctx
        self.bot = ctx.bot
        self.db = ctx.bot.exps
        self.message = None
        self.player1 = self.turn = ctx.author
        self.player2 = member or ctx.me
        self.p1 = self.p2 = ''
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

    @property
    def empty_cells(self):
        cells = []
        for x, row in enumerate(self.board):
            for y, col in enumerate(row):
                if col == 0:
                    cells.append([x, y])

        return cells

    @property
    def game_over(self):
        return self.depth == 0 or self.is_winner(self.HUMAN) or self.is_winner(self.COMP)

    @property
    def depth(self):
        return len(self.empty_cells)

    @property
    def emojis(self):
        return {f'{x}\N{VARIATION SELECTOR-16}'
                '\N{COMBINING ENCLOSING KEYCAP}': x
                for x in range(1, 10)}

    def is_winner(self, player):
        state = self.board
        win_state = []
        diagonals = [[], []]
        for x in range(3):
            row = []
            col = []
            for y in range(3):
                row.append(state[x][y])
                col.append(state[y][x])

            win_state.append(row)
            win_state.append(col)
            diagonals[0].append(state[x][x])
            diagonals[1].append(state[abs(x-2)][x]
                                if x != 1
                                else state[1][1])

        win_state.extend(diagonals)

        return ([player for _ in range(3)] in win_state)

    async def ai_turn(self):
        if self.game_over:
            return True

        if self.depth == 9:
            x = secrets.choice(range(3))
            y = secrets.choice(range(3))
        else:
            move = self.minimax(self.depth, self.COMP)
            x, y, _ = move

        self.set_move(x, y, self.COMP)
        return True

    async def human_turn(self):
        if self.game_over:
            return True

        player, sign = (
            (self.HUMAN, self.p1)
            if self.turn == self.player1
            else (self.COMP, self.p2)
        )
        move = -1
        moves = {}
        n = 0
        for x in range(3):
            for y in range(3):
                n += 1
                moves[n] = [x, y]

        await self.render(f'{self.turn.mention}\'s turn! ({sign})')

        while move < 1 or move > 9:
            try:
                payload = await self.bot.wait_for(
                    'raw_reaction_add',
                    check=(
                        lambda x: x.message_id == self.message.id
                        and x.user_id == self.turn.id
                        and x.emoji.name in self.emojis
                    ),
                    timeout=60
                )

                move = self.emojis[payload.emoji.name]
                coord = moves[move]
                coord.append(player)
                can_move = self.set_move(*coord)

                if not can_move:
                    move = -1

            except TimeoutError:
                return await self.quit()

        return True

    def valid_move(self, x, y):
        return ([x, y] in self.empty_cells)

    def set_move(self, x, y, player):
        if self.valid_move(x, y):
            self.board[x][y] = player
            return True

        return False

    def evaluate(self):
        if self.is_winner(self.COMP):
            return 1

        if self.is_winner(self.HUMAN):
            return -1

        return 0

    def minimax(self, depth, player):
        """
        The actual minimax method
        """
        best = [-1, -1, float('-inf' if player == self.COMP else 'inf')]

        if depth == 0 or self.game_over:
            score = self.evaluate()
            return [-1, -1, score]

        for cell in self.empty_cells:
            x, y = cell
            self.board[x][y] = player   # evaluates
            score = self.minimax(depth - 1, -player)
            self.board[x][y] = 0        # resets to 0
            score[0], score[1] = x, y

            if player == self.COMP:
                if score[2] > best[2]:
                    best = score

            else:
                if score[2] < best[2]:
                    best = score

        return best

    async def render(self, title):
        signs = {
            -1: self.p1,
            1: self.p2
        }

        str_line = '---------------'  # whatever
        board_view = f'```\n{str_line}\n'
        n = 0
        for row in self.board:
            for cell in row:
                n += 1
                sign = signs.get(cell, n)
                board_view += f'| {sign} |'

            board_view += f'\n{str_line}\n'

        board_view += '```'

        embed = Embed(title='Tic Tac Toe', description=board_view)
        if self.message:
            return await self.message.edit(embed=embed, content=title)

        self.message = await self.ctx.send(embed=embed, content=title)
        self.bot.loop.create_task(self.add_reactions())

    async def add_reactions(self):
        for e in self.emojis:
            await self.message.add_reaction(e)

    async def quit(self):
        winner = (self.player1
                  if self.turn != self.player1
                  else self.player2)
        await self.render(f'{self.turn.mention} quit the game, '
                          f'{winner.mention} won!')
        await self.update_xp(winner, self.turn)

    async def update_xp(self, winner, loser):
        if not winner and not loser:
            await self.add_xp(self.player1)
            await self.add_xp(self.player2)
            return

        await self.add_xp(winner)
        await self.reduce_xp(loser)

    async def add_xp(self, winner):
        if winner == self.ctx.me:
            return

        xp = self.db.get(winner.id, 20)
        xp += xp * 10 / 100
        await self.db.put(winner.id, xp)

    async def reduce_xp(self, loser):
        if loser == self.ctx.me:
            return

        xp = self.db.get(loser.id, 20)
        if not xp:
            return

        xp -= xp * 10 / 100
        xp = clamp(xp, 0, float('inf'))
        await self.db.put(loser.id, xp)

    @property
    def is_enemy_human(self):
        return self.player2 != self.ctx.me

    async def start(self):
        try:
            self.p1 = secrets.choice(('X', 'O'))
            if self.p1 == 'X':
                self.p2 = 'O'
            else:
                self.p2 = 'X'

            first = secrets.choice(('n', ''))

            if self.is_enemy_human:
                # case where the enemy is a human
                async def player2_turn():
                    try:
                        self.turn = self.player2  # sets current player to player 2
                        return await self.human_turn()
                    finally:
                        self.turn = self.player1  # set it back to player 1

            else:
                # case where the enemy is a computer
                player2_turn = self.ai_turn
                await self.ctx.send('First to start? [y(es)/n(o)/r(andom)/q(uit)]')

                try:
                    msg = await self.bot.wait_for(
                        'message',
                        check=(
                            lambda x: x.author == self.ctx.author
                            and x.content.lower().startswith(('y', 'n',
                                                              'q', 'r'))
                        ),
                        timeout=60
                    )

                    if (msg := msg.content.lower()).startswith('q'):
                        return await self.ctx.send('You\'ve quit the game')

                    if msg not in ('r', 'random'):
                        first = msg

                except TimeoutError:
                    return await self.ctx.send('You took too long to answer!')

            if first.startswith('n'):
                if not await player2_turn():
                    return

            while not self.game_over:
                if not await self.human_turn():
                    return

                if not await player2_turn():
                    return

            text = '{0.mention} won the game! ({1})'
            if self.is_winner(self.HUMAN):
                winner, loser = self.player1, self.player2
                text = text.format(winner, self.p1)
            elif self.is_winner(self.COMP):
                winner, loser = self.player2, self.player1
                text = text.format(winner, self.p2)
            else:
                text = 'Draw!'
                winner, loser = None, None

            await self.update_xp(winner, loser)
            await self.render(text)

        finally:
            self.bot.ttt_games.remove(self.ctx.channel.id)


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['ttt']
    )
    async def tictactoe(self, ctx, *, member: Member = None):
        """
        Play TicTacToe with your friend!
        You can also play with me, but I doubt you'll win
        """
        if ctx.channel.id in self.bot.ttt_games:
            return await ctx.send('Can only play 1 game in a channel concurrently')

        member = member or ctx.me
        if (
            (member.bot and member != ctx.me)
            or member == ctx.author
        ):
            # case where the author asks a bot to play
            return await ctx.send("You can play with me instead :)")

        if member != ctx.me:
            # case where the author asks a user to play
            await ctx.send(f'{member}, do you want to play with {ctx.author}?')

            try:
                msg = await self.bot.wait_for(
                    'message',
                    check=(
                        lambda x: x.author == member
                        and x.channel.id == ctx.channel.id
                        and x.content.lower().startswith(('y', 'n'))
                    )
                )

                content = msg.content.lower()
                if content.startswith('n'):
                    return await ctx.send(f'{member} refused to play :(')

                if ctx.channel.id in self.bot.ttt_games:
                    # case where the user accepted
                    # but another game is already running
                    return await ctx.send('Can only play 1 game in a channel concurrently')

            except TimeoutError:
                return await ctx.send(f'{member} didn\'t respond')

        game = TicTacToe(ctx, member)
        await game.start()

    @commands.command(
        aliases=['lb']
    )
    async def leaderboard(self, ctx, page: int = None):
        """
        Shows the global leaderboard
        """
        sorted_db = sorted(self.bot.exps.db.items(), key=lambda x: x[1], reverse=True)
        idx = self.find_index(sorted_db, ctx.author.id)
        if idx < 0:
            idx = 0

        content = ''
        page = page - 1 if page is not None else idx // 10
        idx = page * 10
        for i in range(idx, idx+10):
            try:
                user_id, xp = sorted_db[i]
                content += f'{i+1}. <@{user_id}> -> {round(xp, 2)}\n'
            except IndexError:
                break

        if not content:
            return await ctx.send('Page doesn\'t exist!')

        embed = Embed(title='Global Leaderboard', description=content)
        await ctx.send(embed=embed)

    @staticmethod
    def find_index(array, element):
        """
        Binary search method
        """
        mid = 0
        start = 0
        end = len(array)
        step = 0
        while (start <= end):
            step = step + 1
            mid = (start + end) // 2

            if element == int(array[mid][0]):
                return mid

            if element < int(array[mid][0]):
                end = mid - 1
            else:
                start = mid + 1
        return -1


def setup(bot): bot.add_cog(Games(bot))
