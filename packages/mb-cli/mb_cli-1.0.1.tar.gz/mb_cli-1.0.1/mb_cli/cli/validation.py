import re
from prompt_toolkit.validation import ValidationError, Validator

from mb_cli import settings


class CoinAddressValidator(Validator):

    def __init__(self, coin: str):
        self._coin = coin
        self._regex = settings.REGEX_LIST[self._coin]

    def validate(self, document):
        if not len(document.text) > 0:
            raise ValidationError(
                message="Address can't be empty.",
                cursor_position=document.cursor_position
            )

        if not re.match(self._regex, document.text):
            raise ValidationError(
                message=f'Invalid {self._coin} address.',
                cursor_position=document.cursor_position
            )


class LimitAmountValidator(Validator):

    def __init__(self, sell_coin: str, min_amount: float, max_amount: float):
        self._coin = sell_coin
        self._min_amount = min_amount
        self._max_amount = max_amount

    def validate(self, document):

        if not len(document.text) > 0:
            raise ValidationError(
                message="Amount can't be empty.",
                cursor_position=document.cursor_position
            )

        amount = document.text

        if re.match('^\d+(\.(?=\d))?\d*$', amount):
            if not (self._min_amount <= float(amount) <= self._max_amount):
                raise ValidationError(
                    message=f'{self._coin} amount should be higher than {str(self._min_amount).upper()} and lower than {str(self._max_amount).upper()}.',
                    cursor_position=document.cursor_position
                )
        else:
            raise ValidationError(
                message=f'{self._coin} amount should be a number.',
                cursor_position=document.cursor_position
            )
