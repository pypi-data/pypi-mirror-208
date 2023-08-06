#!/usr/bin/python
# -*- coding: utf-8 -*-

# Savage World
# https://fr.wikipedia.org/wiki/Savage_Worlds

from dicencards.dice import BunchOfDice, UNLIMITED_REROLL, BUST, BEST_OF_DICE



ON_MAX_REROLL = UNLIMITED_REROLL
ON_MIN_REROLL = 0

QUALITY = 'QUALITY'
SUCCESS = 'SUCCESS'
FAIL = 'FAIL'
FUMBLE = 'FUMBLE'
RAISE = 'RAISE'
RAISE_COUNT = 'RAISE_COUNT'

RAISE_STEP = 5

FAIR = 5


def check(dice_type:int, number_of_dice:int, target: int):
    bunch = BunchOfDice(number_of_dice, dice_type)
    result = bunch.roll(ON_MAX_REROLL, ON_MIN_REROLL)
    if result[BUST] >= number_of_dice/2:
        result[QUALITY] = FUMBLE
    elif result[BEST_OF_DICE] < target:
        result[QUALITY] = FAIL
    elif result[BEST_OF_DICE] >= target:
        result[QUALITY] = SUCCESS
        raise_count = (result[BEST_OF_DICE] - target) // RAISE_STEP
        result[RAISE_COUNT] = raise_count
        if raise_count > 0:
            result[QUALITY] = RAISE
    return result
