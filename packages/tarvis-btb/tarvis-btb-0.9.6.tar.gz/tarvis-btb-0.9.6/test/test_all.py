import common  # noqa
from decimal import Decimal
import logging
from tarvis.btb import BasicTradingBot, ExchangeAccount
from tarvis.common import time
from tarvis.common.trading import MarketPosition
from tarvis.exchange.test import TestExchange
from tarvis.indicators.test import TestIndicatorSource
import pytest  # noqa


def test_all():
    _BASE_ASSET = "BTC"
    _BASE_ASSET_START_AMOUNT = Decimal("0")
    _QUOTE_ASSET = "USD"
    _QUOTE_ASSET_START_AMOUNT = Decimal("100000")
    _PRICE_INITIAL = Decimal("1000")
    _PRICE_VARIANCE = Decimal("100")
    _PRICE_LOW = _PRICE_INITIAL - _PRICE_VARIANCE
    _PRICE_HIGH = _PRICE_INITIAL + _PRICE_VARIANCE
    _NUM_TRANSITIONS = 20
    _NUM_UPDATE_ITERATIONS = 5
    _START_TIME = 100000
    _STEP_TIME = 5000
    _END_TIME = _START_TIME + ((_NUM_TRANSITIONS + 1) * _STEP_TIME)
    _TRADE_OFFSET = 100
    source = TestIndicatorSource()
    exchange = TestExchange()
    account = ExchangeAccount(exchange, _BASE_ASSET, _QUOTE_ASSET)
    bot = BasicTradingBot(
        source,
        [account],
        base_asset=_BASE_ASSET,
        quote_asset=_QUOTE_ASSET,
        short_selling=True,
        interval=60,
        delay=20,
        retries=0,
        retry_delay=0,
        indicator_expiration=300,
        premium_limit=Decimal("0.0002"),
        stop_loss=Decimal("0.2"),
        reserve=Decimal("1000"),
        leverage_multiplier=1,
        leverage_limit=1,
        watchdog_timeout=5,
    )
    exchange.set_position(_BASE_ASSET, _BASE_ASSET_START_AMOUNT)
    exchange.set_position(_QUOTE_ASSET, _QUOTE_ASSET_START_AMOUNT)

    positions = exchange.get_positions()
    logging.info(f"Balance: {positions}")

    exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_INITIAL)
    for indicator_time in range(_START_TIME, _END_TIME, _STEP_TIME):
        # Ensure that the test ends on a flat so that the quote assets are at a maximum
        if indicator_time == _END_TIME - _STEP_TIME:
            direction = MarketPosition.FLAT
        else:
            direction = source.get_next_direction_transition()
        source.add_simple_indicator(
            _BASE_ASSET, _QUOTE_ASSET, indicator_time, direction
        )
    for simulation_time in range(_START_TIME, _END_TIME, _STEP_TIME):
        trade_time = simulation_time + _TRADE_OFFSET
        time.set_artificial_time(trade_time, 0, allow_reset=True)
        indicator = source.get_indicator(trade_time, _BASE_ASSET, _QUOTE_ASSET)
        match indicator.direction:
            case MarketPosition.FLAT:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_INITIAL)
            case MarketPosition.LONG:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_LOW)
            case MarketPosition.SHORT:
                exchange.set_quote(_BASE_ASSET, _QUOTE_ASSET, _PRICE_HIGH)
        for update_iteration in range(_NUM_UPDATE_ITERATIONS):
            bot._update_account_iteration(account, indicator)
            exchange.fill_orders()
            positions = exchange.get_positions()
            logging.info(f"Balance: {positions}")
    assert positions[_QUOTE_ASSET] > _QUOTE_ASSET_START_AMOUNT
