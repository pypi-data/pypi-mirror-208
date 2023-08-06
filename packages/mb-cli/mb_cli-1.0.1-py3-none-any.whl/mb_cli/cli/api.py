import httpx

from mb_cli import settings


class API:
    def __init__(self, proxy=None, address=settings.CLEAR_DOMAIN):
        self._proxy = proxy
        self._address = address

    def get_rates(self):
        rates = httpx.get(f'{self._address}/rates', proxies=self._proxy)
        return rates.json()

    def get_limits(self, sell_coin):
        rates = httpx.get(f'{self._address}/rates', proxies=self._proxy)
        limits: dict = rates.json()['limits'][sell_coin]
        return limits

        # TODO once API endpoint fixed, replace in get_limits()
        # limits = httpx.post(f'{settings.CLEAR_DOMAIN}/limits', data={'from_currency': sell_coin})
        # return limits.json()

    def calculate_order(self, sell_amount, sell_coin, buy_coin):
        calculation = httpx.post(f'{self._address}/calculate', data={
            'from_amount': sell_amount,
            'from_currency': sell_coin,
            'receive_currency': buy_coin
        }, proxies=self._proxy)
        return calculation.json()

    def create_order(self, sell_amount, sell_coin, buy_coin, buy_address):
        order = httpx.post(f'{self._address}/exchange', data={
            'from_amount': sell_amount,
            'from_currency': sell_coin,
            'receive_currency': buy_coin,
            'receive_address': buy_address,
            'referral_code': settings.MB_REFERRAL
        }, proxies=self._proxy)
        return order.json()

    def track_order(self, order_id):
        order_status = httpx.post(f'{self._address}/track', data={'trx': order_id}, proxies=self._proxy)
        return order_status.json()
