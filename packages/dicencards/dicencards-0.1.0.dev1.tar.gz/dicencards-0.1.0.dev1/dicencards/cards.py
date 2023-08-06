# -*- coding: utf-8 -*-

import random
from enum import Enum
from collections import namedtuple
from dataclasses import dataclass, field


class TupleSymbol(namedtuple('TupleSymbol', ['name', 'glyph'])):

    def __str__(self):
        return f'{self.name}: {self.glyph}'


class TupleColor(namedtuple('TupleColor', ['name', 'repr', 'rgb', 'ansi'])):

    def __str__(self):
        return f'{self.name}: #{self.rgb}'


class TupleSuite(namedtuple('TupleSuite', ['symbol', 'color'])):

    def __str__(self):
        return f'{self.symbol.name}: {self.color.ansi}{self.symbol.glyph}\033[m'


class TupleRank(namedtuple('TupleRank', ['name', 'order', 'repr'])):

    def __str__(self):
        return f'{self.name}: {self.order}'


class Symbol(Enum):
    CLUBS = TupleSymbol('club', '\u2663')
    DIAMONDS = TupleSymbol('diamonds', '\u2666')
    HEARTS = TupleSymbol('hearts', '\u2665')
    SPADES = TupleSymbol('spades', '\u2660')

    def glyph(self):
        return self.value.glyph

    def __str__(self):
        return str(self.value)


class Color(Enum):
    BLACK = TupleColor('black', 'B', '000000', '\033[30m')
    RED = TupleColor('red', 'R', 'FF0000', '\033[31m')

    def ansi(self):
        return self.value.ansi

    def rgb(self):
        return self.value.rgb

    def __str__(self):
        # return f'{self.value.ansi}{self.name}\0033[m'
        return self.value.repr


class Suite(Enum):
    CLUBS = TupleSuite(Symbol.CLUBS, Color.BLACK)
    DIAMONDS = TupleSuite(Symbol.DIAMONDS, Color.RED)
    HEARTS = TupleSuite(Symbol.HEARTS, Color.RED)
    SPADES = TupleSuite(Symbol.SPADES, Color.BLACK)

    def symbol(self) -> Symbol:
        return self.value.symbol

    def color(self) -> Color:
        return self.value.color

    def glyph(self):
        return self.value.symbol.glyph()

    def colored_glyph(self):
        return f'{self.color().ansi()}{self.glyph()}\033[m'

    def __str__(self):
        return self.colored_glyph()


class Rank(Enum):
    ONE = TupleRank('one', 1, '1')
    TWO = TupleRank('two', 2, '2')
    THREE = TupleRank('three', 3, '3')
    FOUR = TupleRank('four', 4, '4')
    FIVE = TupleRank('five', 5, '5')
    SIX = TupleRank('six', 6, '6')
    SEVEN = TupleRank('seven', 7, '7')
    EIGHT = TupleRank('eight', 8, '8')
    NINE = TupleRank('nine', 9, '9')
    TEN = TupleRank('ten', 10, '10')
    JACK = TupleRank('jack', 11, 'J')
    KNIGHT = TupleRank('knight', 12, 'C')
    QUEEN = TupleRank('queen', 13, 'Q')
    KING = TupleRank('king', 14, 'K')
    ACE = TupleRank('ace', 15, 'A')
    JOKER = TupleRank('joker', 20, 'Jo')

    def __str__(self):
        return str(self.value.repr)


@dataclass
class Card:
    rank: Rank
    suite: Suite = field(default=None)
    color: Color = field(default=None)

    def __post_init__(self):
        # TODO: Tester la cohérence
        if self.suite is not None:
            self.color = self.suite.color()

    def __eq__(self, other):
        return self.rank == other.rank and self.suite == other.suite

    def __str__(self):
        if self.suite is None:
            s = f'{self.rank}{self.color}'.rjust(3)
        else:
            s = f'{self.rank}{self.suite}'.rjust(3)
        return s


class ValueModel:
    ASC = 1
    DESC = -1

    def __init__(self):
        pass

    def evaluate(self, card: Card):
        raise NotImplementedError()

    def compare(self, c1, c2):
        c1_val = self.evaluate(c1)
        c2_val = self.evaluate(c2)
        if c1_val > c2_val:
            return 1
        elif c1_val < c2_val:
            return -1
        else:
            return 0

    def sort(self, cards, order=ASC):
        evaluated_cards = []
        for card in cards:
            evaluated_cards.append((card, self.evaluate(card)))
        evaluated_cards = sorted(evaluated_cards, key=lambda c: c[1])
        # print(' | '.join('{}={}'.format(str(c[0]), c[1]) for c in evaluated_cards))
        sorted_card = []
        for evaluated_card in evaluated_cards:
            sorted_card.append(evaluated_card[0])
        if order == ValueModel.DESC:
            sorted_card.reverse()
        return sorted_card


class Deck:

    def __init__(self, cards: list[Card]):
        self.cards: list[Card] = cards

    def __str__(self):
        return ' |'.join(str(c) for c in self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n) -> list[Card]:
        subset: list[Card] = []
        i = 0
        while i < n:
            subset.append(self.cards.pop(0))
            i += 1
        return subset

    def count(self):
        """Count cards in the deck"""
        return len(self.cards)

    def sort(self, value_model: ValueModel, order: int = ValueModel.ASC):
        """Sorts the cards in the deck regarding the specified value model"""
        self.cards = value_model.sort(self.cards, order)


class BasicValueModel(ValueModel):

    def __init__(self):
        super().__init__()
        self.model = {}
        value = 1
        for rank in list(Rank):
            self.model[rank] = value
            value += 1

    def evaluate(self, card: Card):
        return self.model.get(card.rank, 0)
