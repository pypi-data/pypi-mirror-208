#!/usr/bin/python
# -*- coding: utf-8 -*-

# D6 System
# https://fr.wikipedia.org/wiki/D6_System

# Difficultés
# 0     Automatique
# 1–5   Très Facile
# 6–10  Facile
# 11–15 Moyenne
# 16–20 Difficile
# 21–25 Très difficile
# 26–30 Héroïque
# >31   Légendaire
#
# Marge de réussite
# 0     Minime
# 1-4   Basique
# 5-8   Bon
# 9-12  Supérieur
# 13-16 Spectaculaire
# >16 Incroyable

from dicencards.dice import BunchOfDice, UNLIMITED_REROLL, BUST, SCORES, SUM_OF_DICE

_DICE_TYPE: int = 6

QUALITY = 'QUALITY'
SUCCESS = 'SUCCESS'
FAIL = 'FAIL'
FUMBLE = 'FUMBLE'
MARGIN = 'MARGIN'


def check(number_of_dice: int, target: int, bonus: int = 0):
    normal_dies = BunchOfDice(number_of_dice - 1, _DICE_TYPE)
    joker_dice = BunchOfDice(1, _DICE_TYPE)

    normal_result = normal_dies.roll()
    joker_result = joker_dice.roll(UNLIMITED_REROLL)

    scores = joker_result[SCORES].extend(normal_result[SCORES])

    total = sum(scores) + bonus

    quality = FAIL

    if joker_result[BUST] > 0:
        quality = FUMBLE
        max_score = max(scores)
        total = total - max_score
    elif total >= target:
        quality = SUCCESS

    margin = target - total

    return {SCORES: scores, SUM_OF_DICE: total, QUALITY: quality, MARGIN: margin}
