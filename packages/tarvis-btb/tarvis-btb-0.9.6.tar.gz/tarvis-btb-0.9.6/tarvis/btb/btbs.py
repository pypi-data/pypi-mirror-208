import tarvis.common.logging


def run(
    indicator_source_classes,
    exchange_classes,
    additional_providers=None,
    additional_modules=None,
):
    import logging

    try:
        from dependency_injector import containers, providers
        import tarvis.common.config
        import tarvis.common.monitoring
        import tarvis.common.secrets
        import sys
        from . import BasicTradingBot, ExchangeAccount

        container = containers.DynamicContainer()
        container.config = tarvis.common.config.Configuration()
        container.watchdog = providers.ThreadSafeSingleton(
            tarvis.common.monitoring.Watchdog
        )

        if additional_providers:
            for name, provider in additional_providers:
                setattr(container, name, provider)

        if additional_modules is None:
            additional_modules = []

        container.wire(
            modules=[
                __name__,
                tarvis.common.config,
                tarvis.common.logging,
                tarvis.common.monitoring,
                tarvis.common.secrets,
                tarvis.btb.basictradingbot,
                *additional_modules,
            ]
        )

        # Adjust logging after configuration is available
        tarvis.common.logging.load_config()

        indicator_source_class_map = {}
        for indicator_source_class in indicator_source_classes:
            indicator_source_class_map[
                indicator_source_class.INDICATOR_SOURCE_NAME
            ] = indicator_source_class

        exchange_class_map = {}
        for exchange_class in exchange_classes:
            exchange_class_map[exchange_class.EXCHANGE_NAME] = exchange_class

        bots = container.config.bots()
        bot_threads = []

        if not bots:
            logging.error("No bots defined.")
        else:
            for bot_config in bots:
                indicator_source_config = bot_config.pop("indicator_source")
                indicator_source_name = indicator_source_config.pop("name")
                indicator_source_class = indicator_source_class_map.get(
                    indicator_source_name
                )

                if indicator_source_class is None:
                    raise ValueError(
                        f"indicator_source {indicator_source_name} not recognized."
                    )
                else:
                    indicator_source = indicator_source_class(**indicator_source_config)

                    accounts_config = bot_config.pop("accounts")
                    accounts = []

                    for account_config in accounts_config:
                        exchange_config = account_config.pop("exchange")
                        exchange_name = exchange_config.pop("name")

                        exchange_class = exchange_class_map.get(exchange_name)
                        if exchange_class is None:
                            raise ValueError(
                                f"exchange {exchange_name} not recognized."
                            )

                        exchange = exchange_class(**exchange_config)

                        account = ExchangeAccount(exchange, **account_config)
                        accounts.append(account)

                    if len(accounts) == 0:
                        raise ValueError("No accounts defined.")

                    bot_config["indicator_source"] = indicator_source
                    bot_config["accounts"] = accounts
                    bot = BasicTradingBot(**bot_config)
                    bot_threads.append(bot.start())

        if len(bot_threads) == 0:
            logging.critical("No bots started.")
        else:
            for thread in bot_threads:
                thread.join()

    except Exception as unhandled_exception:
        logging.critical(f"Unhandled exception: {unhandled_exception}", exc_info=True)
        _EXIT_FAILURE = 1
        exit(_EXIT_FAILURE)
