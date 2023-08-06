from dependency_injector.wiring import Provide, inject
from decimal import Decimal
import logging
from tarvis.common import time
from tarvis.common.monitoring import WatchdogLogTimer
from tarvis.common.trading import (
    BasicTradingIndicator,
    BasicTradingIndicatorSource,
    MarketPosition,
    OrderSide,
    OrderType,
)
from threading import Thread
from . import ExchangeAccount


class BasicTradingBot:
    @inject
    def __init__(
        self,
        indicator_source: BasicTradingIndicatorSource,
        accounts: list[ExchangeAccount],
        base_asset: str,
        quote_asset: str,
        short_selling: bool,
        interval: float,
        delay: float,
        retries: int,
        retry_delay: float,
        indicator_expiration: float,
        price_deviation_limit: float,
        premium_limit: Decimal,
        stop_loss: Decimal,
        watchdog_timeout: float,
        watchdog=Provide["watchdog"],
    ):
        """
        :param price_deviation_limit: percentage (i.e. 0.00025 is 0.025% deviation)
        :param premium_limit: percentage (i.e. 0.00025 is 0.025% premium)
        :param stop_loss: percentage (i.e. 0.2 is 20%), 0 is none
        """
        short_selling = bool(short_selling)
        interval = float(interval)
        if interval <= 0:
            raise ValueError("interval must be greater than 0.")
        delay = float(delay)
        if delay <= 0:
            raise ValueError("delay must be greater than 0.")
        if delay >= interval:
            raise ValueError("delay must be less than interval.")
        retries = int(retries)
        if retries < 0:
            raise ValueError("retries must be greater than or equal to 0.")
        retry_delay = float(retry_delay)
        if (retries * retry_delay) >= interval:
            raise ValueError(
                "The product of retries and retry_delay must be less than the interval."
            )
        indicator_expiration = float(indicator_expiration)
        if indicator_expiration <= 0:
            raise ValueError("indicator_expiration must be greater than 0.")
        price_deviation_limit = float(price_deviation_limit)
        if (price_deviation_limit < 0) or (price_deviation_limit >= 1):
            raise ValueError(
                "price_deviation_limit must be equal to 0 or greater than 0 and less than 1."
            )
        premium_limit = Decimal(premium_limit)
        if (premium_limit < 0) or (premium_limit >= 1):
            raise ValueError(
                "premium_limit must be equal to 0 or greater than 0 and less than 1."
            )
        stop_loss = Decimal(stop_loss)
        if (stop_loss < 0) or (stop_loss >= 1):
            raise ValueError(
                "stop_loss must be equal to 0 or greater than 0 and less than 1."
            )
        watchdog_timeout = float(watchdog_timeout)
        if watchdog_timeout < interval:
            raise ValueError("watchdog_timeout must be greater than interval.")

        self._logger = logging.getLogger(self.__class__.__name__)
        self._indicator_source = indicator_source
        self._accounts = accounts
        self._indicator_base_asset = base_asset
        self._indicator_quote_asset = quote_asset
        self._short_selling = short_selling
        self._interval = interval
        self._delay = delay
        self._retries = retries
        self._retry_delay = retry_delay
        self._indicator_expiration = indicator_expiration
        self._price_deviation_limit = price_deviation_limit
        self._premium_limit = premium_limit
        self._stop_loss = stop_loss
        self._log_extra = {
            "indicator_source": indicator_source.INDICATOR_SOURCE_NAME,
            "indicator_base_asset": base_asset,
            "indicator_quote_asset": quote_asset,
            "interval": interval,
        }
        self._watchdog_timeout = watchdog_timeout
        self._watchdog = watchdog
        self._watchdog_timer = WatchdogLogTimer(
            watchdog_timeout, logging.ERROR, self.__class__.__name__, self._log_extra
        )
        self._watchdog.add_timer(self._watchdog_timer)
        self._accounts_threads = {}

    def _update_account_iteration(
        self, account: ExchangeAccount, indicator: BasicTradingIndicator
    ) -> bool:
        exchange = account.exchange
        base_asset = account.base_asset
        quote_asset = account.quote_asset
        log_extra_iteration = {
            **self._log_extra,
            "indicator_time": indicator.time,
            "indicator_direction": indicator.direction.name,
            "exchange": exchange.EXCHANGE_NAME,
            "exchange_base_asset": base_asset,
            "exchange_quote_asset": quote_asset,
        }
        if indicator.price:
            log_extra_iteration["indicator_price"] = indicator.price

        match indicator.direction:
            case MarketPosition.FLAT:
                order_side_opposing = None
                price_deviation_limit = 0
                price_allowance = 0
                stop_loss_price_ratio = None
            case MarketPosition.LONG:
                order_side_opposing = OrderSide.SELL
                price_deviation_limit = 1 + self._price_deviation_limit
                price_allowance = 1 + self._premium_limit
                stop_loss_price_ratio = 1 - self._stop_loss
            case MarketPosition.SHORT:
                order_side_opposing = OrderSide.BUY
                price_deviation_limit = 1 - self._price_deviation_limit
                price_allowance = 1 - self._premium_limit
                stop_loss_price_ratio = 1 + self._stop_loss
            case _:
                raise ValueError("Indicator direction is invalid.")

        positions = exchange.get_positions()
        base_asset_position = positions.get(base_asset, 0)
        orders = exchange.get_open_orders(base_asset, quote_asset)
        quote_price = exchange.get_quote(base_asset, quote_asset)
        trading_policy = exchange.get_policy(base_asset, quote_asset)
        minimum_order_quantity = trading_policy.get_minimum_order_quantity(quote_price)
        flatten_vector = 0
        direction_vector = 0
        stop_loss_orders = []
        stop_loss_vector = 0

        for order in orders:
            cancel_order = False
            order_vector = order.get_quantity(quote_price) - order.filled_quantity

            # Cancel all (except stop loss) orders placed before the indicator
            if (order.creation_time < indicator.time) and (
                order.order_type != OrderType.STOP_LOSS
            ):
                cancel_order = True

            # Cancel all orders that are not market orders if indicator is flat
            elif (indicator.direction == MarketPosition.FLAT) and (
                order.order_type != OrderType.MARKET
            ):
                cancel_order = True

            # Cancel all stop loss orders that are not against the
            elif (order.order_type == OrderType.STOP_LOSS) and (
                order.side != order_side_opposing
            ):
                cancel_order = True

            else:
                if order.side == OrderSide.BUY:
                    order_vector = order_vector
                else:
                    order_vector = -order_vector

                # Only cancel the market orders that are not flattening
                if order.order_type == OrderType.MARKET:
                    # Cancel all sell orders if current position is short
                    # Cancel all buy orders if current position is long
                    # Tally the flattening orders
                    if (
                        (order.side == OrderSide.BUY) and (base_asset_position >= 0)
                    ) or (
                        (order.side == OrderSide.SELL) and (base_asset_position <= 0)
                    ):
                        cancel_order = True
                    else:
                        flatten_vector += order_vector

                # Tally the directional and stop loss orders
                elif order.order_type == OrderType.LIMIT:
                    direction_vector += order_vector
                elif order.order_type == OrderType.STOP_LOSS:
                    stop_loss_orders.append(order)
                    stop_loss_vector += order_vector

            if cancel_order:
                # noinspection PyProtectedMember
                self._logger.info(
                    "Cancelling order.",
                    extra={
                        **log_extra_iteration,
                        "order_side": order.side.name,
                        "order_type": order.order_type.name,
                        "order_quantity": str(order._quantity),
                        "order_amount": str(order._amount),
                    },
                )
                exchange.cancel_order(order)

        opposing_position = base_asset_position + flatten_vector
        match indicator.direction:
            case MarketPosition.LONG:
                if opposing_position > 0:
                    opposing_position = 0
            case MarketPosition.SHORT:
                if opposing_position < 0:
                    opposing_position = 0
        flatten_quantity = abs(trading_policy.align_quantity(opposing_position))

        if (flatten_quantity != 0) and (flatten_quantity >= minimum_order_quantity):
            flatten_quantity = trading_policy.limit_quantity_maximum(
                flatten_quantity, quote_price
            )
            if opposing_position > 0:
                flatten_order_side = OrderSide.SELL
            else:
                flatten_order_side = OrderSide.BUY
            self._logger.info(
                "Placing flattening order.",
                extra={
                    **log_extra_iteration,
                    "order_side": flatten_order_side.name,
                    "order_quantity": str(flatten_quantity),
                },
            )
            exchange.place_order(
                trading_policy,
                base_asset,
                quote_asset,
                flatten_order_side,
                OrderType.MARKET,
                flatten_quantity,
                price=quote_price,
                increasing_position=False,
            )
            return False

        if indicator.direction == MarketPosition.FLAT:
            return True

        else:
            # If indicator has expired or is impossible to complete, do not move
            if (time.time() > (indicator.time + self._indicator_expiration)) or (
                (indicator.direction == MarketPosition.SHORT)
                and (
                    (not self._short_selling) or (not exchange.short_selling_supported)
                )
            ):
                direction_completed = True

            # If the quoted price deviates too far from the indicator, do not move
            elif (indicator.price is not None) and (
                (
                    (indicator.direction == MarketPosition.LONG)
                    and (quote_price > (indicator.price * price_deviation_limit))
                )
                or (
                    (indicator.direction == MarketPosition.SHORT)
                    and (quote_price < (indicator.price * price_deviation_limit))
                )
            ):
                self._logger.info(
                    "Directional order not placed due to excessive price deviation.",
                    extra={
                        **log_extra_iteration,
                        "quote_price": str(quote_price),
                    },
                )
                direction_completed = True

            # Otherwise, attempt to move in the direction
            else:
                quote_asset_position = positions.get(quote_asset, 0)

                order_price = quote_price * price_allowance
                order_price = trading_policy.align_price(order_price)

                # Value is in quote asset price
                base_value = base_asset_position * quote_price
                total_value = quote_asset_position + base_value
                available_value = total_value - account.reserve
                if (account.position_limit is not None) and (
                    available_value > account.position_limit
                ):
                    available_value = account.position_limit

                leverage = indicator.leverage * account.leverage_multiplier
                if leverage > account.leverage_limit:
                    leverage = account.leverage_limit

                current_ratio = abs(base_value) / available_value
                desired_ratio = Decimal((1 - indicator.take_profit) * leverage)

                order_ratio = desired_ratio - current_ratio
                order_vector = order_ratio * available_value / order_price

                if indicator.direction == MarketPosition.SHORT:
                    order_vector = -order_vector

                order_vector -= direction_vector
                order_vector = trading_policy.align_quantity(order_vector)
                if order_vector > 0:
                    order_side = OrderSide.BUY
                else:
                    order_side = OrderSide.SELL
                order_quantity = abs(order_vector)

                # If there is no profit taking, then do not move against the position
                if (indicator.take_profit == 0) and (order_side == order_side_opposing):
                    direction_completed = True

                # If profit taking has begun, do not move further into the position
                elif (indicator.take_profit > 0) and (
                    order_side != order_side_opposing
                ):
                    direction_completed = True

                # If profit taking, do not move further until previous orders complete
                elif (direction_vector != 0) and (indicator.take_profit > 0):
                    direction_completed = True

                # If the order quantity does not meet the minimum, do not order
                elif (order_quantity == 0) or (order_quantity < minimum_order_quantity):
                    direction_completed = True

                # Otherwise, place a limit order to move in the direction
                else:
                    direction_completed = False

                    # Some exchanges will automatically create stop losses when an order
                    # is filled
                    if self._stop_loss == 0:
                        stop_loss_price = None
                    else:
                        stop_loss_price = quote_price * stop_loss_price_ratio
                        stop_loss_price = trading_policy.align_price(stop_loss_price)

                    order_quantity = trading_policy.limit_quantity_maximum(
                        order_quantity, order_price
                    )
                    self._logger.info(
                        "Placing directional order.",
                        extra={
                            **log_extra_iteration,
                            "order_side": order_side.name,
                            "order_quantity": str(order_quantity),
                            "order_price": str(order_price),
                            "order_amount": str(order_quantity * order_price),
                        },
                    )
                    exchange.place_order(
                        trading_policy,
                        base_asset,
                        quote_asset,
                        order_side,
                        OrderType.LIMIT,
                        order_quantity,
                        price=order_price,
                        stop_loss_price=stop_loss_price,
                        increasing_position=True,
                    )

            # If stop loss is not possible or requested, do not add a stop loss
            if (not exchange.stop_loss_orders_supported) or (self._stop_loss == 0):
                stop_loss_completed = True

            # If the direction has not been achieved, no stop loss is needed
            elif (
                (indicator.direction == MarketPosition.LONG)
                and (base_asset_position <= 0)
            ) or (
                (indicator.direction == MarketPosition.SHORT)
                and (base_asset_position >= 0)
            ):
                stop_loss_completed = True

            # Otherwise, add or adjust the stop loss
            else:
                stop_loss_position = base_asset_position + stop_loss_vector
                stop_loss_excessive = (
                    (indicator.direction == MarketPosition.LONG)
                    and (stop_loss_position < 0)
                ) or (
                    (indicator.direction == MarketPosition.SHORT)
                    and (stop_loss_position > 0)
                )
                stop_loss_quantity = abs(
                    trading_policy.align_quantity(stop_loss_position)
                )

                stop_loss_completed = (not stop_loss_excessive) and (
                    stop_loss_quantity < minimum_order_quantity
                )

                if stop_loss_excessive:
                    order = stop_loss_orders.pop()
                    # noinspection PyProtectedMember
                    self._logger.info(
                        "Cancelling excessive stop-loss order.",
                        extra={
                            **log_extra_iteration,
                            "order_side": order.side.name,
                            "order_type": order.order_type.name,
                            "order_quantity": str(order._quantity),
                            "order_amount": str(order._amount),
                        },
                    )
                    exchange.cancel_order(order)

                elif stop_loss_quantity >= minimum_order_quantity:
                    stop_loss_price = quote_price * stop_loss_price_ratio
                    stop_loss_price = trading_policy.align_price(stop_loss_price)
                    stop_loss_quantity = trading_policy.limit_quantity_maximum(
                        stop_loss_quantity, stop_loss_price
                    )
                    self._logger.info(
                        "Placing stop loss order.",
                        extra={
                            **log_extra_iteration,
                            "order_side": order_side_opposing.name,
                            "order_quantity": str(stop_loss_quantity),
                            "order_price": str(stop_loss_price),
                        },
                    )
                    exchange.place_order(
                        trading_policy,
                        base_asset,
                        quote_asset,
                        order_side_opposing,
                        OrderType.STOP_LOSS,
                        stop_loss_quantity,
                        stop_loss_price=stop_loss_price,
                        increasing_position=False,
                    )

            return direction_completed and stop_loss_completed

    def _update_account(
        self, account: ExchangeAccount, indicator: BasicTradingIndicator
    ) -> None:
        exchange = account.exchange
        base_asset = account.base_asset
        quote_asset = account.quote_asset
        log_extra_update = {
            **self._log_extra,
            "indicator_time": indicator.time,
            "indicator_direction": indicator.direction.name,
            "exchange": exchange.EXCHANGE_NAME,
            "exchange_base_asset": base_asset,
            "exchange_quote_asset": quote_asset,
        }

        self._logger.debug(
            f"Exchange {exchange.EXCHANGE_NAME} {base_asset}/{quote_asset} updating.",
            extra=log_extra_update,
        )

        exchange_watchdog_timer = WatchdogLogTimer(
            self._watchdog_timeout,
            logging.ERROR,
            self.__class__.__name__,
            log_extra_update,
        )
        self._watchdog.add_timer(exchange_watchdog_timer)

        completed = False
        retries = self._retries
        while (not completed) and (retries >= 0):
            try:
                retries -= 1
                exchange_watchdog_timer.reset()

                completed = self._update_account_iteration(account, indicator)

            except Exception as unhandled_exception:
                self._logger.critical(
                    f"Unhandled exception: {unhandled_exception}",
                    extra=log_extra_update,
                    exc_info=True,
                )

            if (not completed) and (retries >= 0):
                time.sleep(self._retry_delay)

        if not completed:
            self._logger.error(
                f"Exchange {exchange.EXCHANGE_NAME} {base_asset}/{quote_asset} "
                f"failed updating after {self._retries} retries.",
                extra=log_extra_update,
            )

        self._watchdog.remove_timer(exchange_watchdog_timer)

    def _trade(self) -> None:
        while True:
            try:
                self._watchdog_timer.reset()

                indicator = self._indicator_source.get_indicator(
                    time.time(), self._indicator_base_asset, self._indicator_quote_asset
                )

                if indicator is None:
                    self._logger.warning("No Indicator.", extra=self._log_extra)
                else:
                    for account in self._accounts:
                        account_thread = self._accounts_threads.pop(account, None)
                        if (account_thread is not None) and account_thread.is_alive():
                            exchange_name = account.exchange.EXCHANGE_NAME
                            base_asset = account.base_asset
                            quote_asset = account.quote_asset
                            self._logger.warning(
                                f"Exchange {exchange_name} {base_asset}/{quote_asset} "
                                "is still updating from last interval.",
                                extra={
                                    **self._log_extra,
                                    "exchange": exchange_name,
                                    "exchange_base_asset": base_asset,
                                    "exchange_quote_asset": quote_asset,
                                },
                            )
                        else:
                            account_thread = Thread(
                                target=self._update_account, args=(account, indicator)
                            )
                            account_thread.start()

                        self._accounts_threads[account] = account_thread

            except Exception as unhandled_exception:
                self._logger.critical(
                    f"Unhandled exception: {unhandled_exception}",
                    extra=self._log_extra,
                    exc_info=True,
                )

            next_time = time.next_interval(time.time(), self._interval)
            next_time += self._delay
            time.sleep_until(next_time)

    def start(self) -> Thread:
        accounts_text = []
        accounts_list = []
        for account in self._accounts:
            exchange_name = account.exchange.EXCHANGE_NAME
            base_asset = account.base_asset
            quote_asset = account.quote_asset
            accounts_text.append(f"{exchange_name}: {base_asset}/{quote_asset}")
            accounts_list.append(
                {
                    "exchange": exchange_name,
                    "exchange_base_asset": base_asset,
                    "exchange_quote_asset": quote_asset,
                }
            )
        self._logger.info(
            f"Starting trading with indicator {self._indicator_base_asset}/{self._indicator_quote_asset} "
            f"on accounts {accounts_text} every {self._interval} seconds.",
            extra={**self._log_extra, "accounts": accounts_list},
        )
        trading_thread = Thread(target=self._trade)
        trading_thread.start()
        return trading_thread
