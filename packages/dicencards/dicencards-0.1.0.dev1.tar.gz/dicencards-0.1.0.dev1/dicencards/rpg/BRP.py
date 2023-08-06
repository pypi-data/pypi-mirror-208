# Basic Role-Playing
# https://fr.wikipedia.org/wiki/Basic_Role-Playing

from dicencards.dice import BunchOfDice, BUST, BEST_OF_DICE

DICE_TYPE = 100
NUMBER_OF_DICE = 1
ON_MAX_REROLL = 0
ON_MIN_REROLL = 0

QUALITY = 'QUALITY'
SUCCESS = 'SUCCESS'
FAIL = 'FAIL'
FUMBLE = 'FUMBLE'
CRITICAL = 'CRITICAL'
SPECIAL = 'SPECIAL'


class BRD:

    def check(self, target: int):
        bunch = BunchOfDice(NUMBER_OF_DICE, DICE_TYPE)
        result = bunch.roll(ON_MAX_REROLL, ON_MIN_REROLL)
        if result[BEST_OF_DICE] <= target:
            result[QUALITY] = self._compute_success_quality(result[BEST_OF_DICE], target)
        else:
            result[QUALITY] = self._compute_failure_quality(result[BEST_OF_DICE], target)
        return result

    def opposition_check(self, active_char: int, passive_char: int):
        target: int = 50 - 5 * passive_char + 5 * active_char
        return self.check(target)

    def _compute_success_quality(self, score: int, target: int):
        quality = SUCCESS
        if score == 1:
            quality = CRITICAL
        return quality

    def _compute_failure_quality(self, score: int, target: int):
        quality = FAIL
        if score == 1:
            quality = FUMBLE
        return quality


class RuneQuest(BRD):
    # réussite critique : jet inférieur ou égal à un vingtième des chances de réussite ;
    # réussite spéciale : jet inférieur ou égal à un cinquième des chances de réussite ;
    # échec critique : jet supérieur à (95 + chances de réussite critique).

    def _compute_success_quality(self, score: int, target: int):
        quality = SUCCESS
        if score <= target // 20:
            quality = CRITICAL
        elif score <= target // 5:
            quality = SPECIAL
        return quality

    def _compute_failure_quality(self, score: int, target: int):
        quality = FAIL
        if score > 95 + target // 20:
            quality = FUMBLE
        return quality
