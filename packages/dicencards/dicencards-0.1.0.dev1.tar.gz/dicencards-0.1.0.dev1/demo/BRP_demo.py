#!/usr/bin/python
# -*- coding: utf-8 -*-

from dicencards.rpg.BRP import BRD, RuneQuest

game = RuneQuest()

print('Running 20 check against target: 50')
i = 0
while i < 20:
    print(game.check(50))
    i = i + 1


print('Running 1 opposition check')
print(game.opposition_check(70, 50))
