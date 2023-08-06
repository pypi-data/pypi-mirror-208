from decimal import Decimal
from tarvis.common.trading import Exchange


class ExchangeAccount:
    def __init__(
        self,
        exchange: Exchange,
        base_asset: str,
        quote_asset: str,
        reserve: Decimal = 0,
        position_limit: Decimal = None,
        leverage_multiplier: float = 1,
        leverage_limit: float = 1,
    ):
        reserve = Decimal(reserve)
        if reserve < 0:
            raise ValueError("reserve must be greater than or equal to 0.")
        if position_limit is not None:
            position_limit = Decimal(position_limit)
            if position_limit <= 0:
                raise ValueError("position_limit must be greater than 0.")
        leverage_multiplier = float(leverage_multiplier)
        if leverage_multiplier <= 0:
            raise ValueError("leverage_multiplier must be greater than 0.")
        leverage_limit = float(leverage_limit)
        if leverage_limit <= 0:
            raise ValueError("leverage_limit must be greater than 0.")

        self.exchange = exchange
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.reserve = Decimal(reserve)
        self.position_limit = position_limit
        self.leverage_multiplier = leverage_multiplier
        self.leverage_limit = leverage_limit
