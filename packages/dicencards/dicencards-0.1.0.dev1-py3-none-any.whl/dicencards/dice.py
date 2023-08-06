#!/usr/bin/python
# -*- coding: utf-8 -*-

import random

__author__ = 'Xavier ROY'

BEST_OF_DICE = 'BEST_OF'

SUM_OF_DICE = 'SUM'

SCORES = 'SCORES'

BUST = 'BUST'

HIT = 'HIT'

UNLIMITED_REROLL = -1

NO_REROLL = 0


class Die:

    def __init__(self, side_count):
        self.side_count = side_count

    def __str__(self):
        return 'D{}'.format(self.side_count)

    def roll(self, on_max_reroll=0, on_min_reroll=0):
        score = random.randint(1, self.side_count)
        if score == self.side_count and on_max_reroll != 0:
            score = score + self.roll(on_max_reroll - 1, False)
        elif score == 1 and on_min_reroll != 0:
            score = score - self.roll(on_min_reroll - 1, False)
        return score


D2 = Die(2)
D4 = Die(4)
D6 = Die(6)
D8 = Die(8)
D10 = Die(10)
D12 = Die(12)
D20 = Die(20)
D100 = Die(100)


class BunchOfDice:

    def __init__(self, number_of_dice: int, die_type: int = 6):
        self.dice = []
        self._die_type = die_type
        for i in range(0, number_of_dice):
            self.dice.append(Die(die_type))

    def __str__(self):
        return '{}D{}'.format(len(self.dice), self._die_type)

    def count_dice(self):
        return len(self.dice)

    def roll(self, on_max_reroll=NO_REROLL, on_min_reroll=NO_REROLL):
        scores = []
        hit_count = 0
        bust_count = 0
        for die in self.dice:
            score = die.roll(on_max_reroll, on_min_reroll)
            if score <= 1:
                bust_count += 1
            elif score >= die.side_count:
                hit_count += 1
            scores.append(score)
        scores = sorted(scores)
        return {SCORES: scores, SUM_OF_DICE: sum(scores), BEST_OF_DICE: max(scores), HIT: hit_count, BUST: bust_count}
