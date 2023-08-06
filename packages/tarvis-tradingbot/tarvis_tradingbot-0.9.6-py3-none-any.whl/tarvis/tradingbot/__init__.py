from tarvis.btb import btbs
import tarvis.exchange.dydx
import tarvis.exchange.woo
import tarvis.indicators.webapi
from tarvis.indicators.webapi import WebAPIIndicatorSource


def main():
    btbs.run(
        indicator_source_classes=[WebAPIIndicatorSource],
        exchange_classes=[
            tarvis.exchange.dydx.DYDXExchange,
            tarvis.exchange.woo.WooExchange,
        ],
        additional_providers=None,
        additional_modules=[tarvis.indicators.webapi],
    )


if __name__ == "__main__":
    main()
