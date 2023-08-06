import logging
import requests
from tarvis.common.trading import (
    BasicTradingIndicator,
    BasicTradingIndicatorSource,
    MarketPosition,
)


class WebAPIIndicatorSource(BasicTradingIndicatorSource):
    INDICATOR_SOURCE_NAME = "WebAPI"

    def __init__(
        self,
        base_url: str,
        params: dict[str, str] = None,
        headers: dict[str, str] = None,
    ):
        self._base_url = base_url
        self._params = params
        self._headers = headers
        super().__init__()

    def get_indicator(
        self,
        sample_time: float,
        base_asset: str,
        quote_asset: str,
    ) -> BasicTradingIndicator | None:
        url = self._base_url.format(
            sample_time=sample_time, base_asset=base_asset, quote_asset=quote_asset
        )
        params = {
            "sample_time": str(sample_time),
            "base_asset": base_asset,
            "quote_asset": quote_asset,
        }
        if self._params:
            params.update(self._params)

        response = requests.get(url, params=params, headers=self._headers)

        if not str(response.status_code).startswith("2"):
            if response.status_code == requests.codes.forbidden:
                logging.error(
                    "WebAPI indicator authentication failure",
                    extra={"url": url, "params": params, "headers": self._headers},
                )
                return None
            elif response.status_code == requests.codes.too_many_requests:
                logging.warning(
                    "WebAPI indicator received too many requests",
                    extra={"url": url, "params": params, "headers": self._headers},
                )
                return None
            else:
                response.raise_for_status()

        data = response.json()

        if not data:
            return None
        else:
            indicator_time = data["time"]
            indicator_time = float(indicator_time)
            position = data["position"]
            position = MarketPosition[position.upper()]
            price = data.get("price")
            if price is not None:
                price = float(price)
            leverage = data.get("leverage", 1)
            leverage = float(leverage)
            take_profit = data.get("take_profit", 0)
            take_profit = float(take_profit)
            meta_data = data.get("meta_data")
            return BasicTradingIndicator(
                indicator_time, position, price, leverage, take_profit, meta_data
            )

    async def get_indicator_async(
        self,
        sample_time: float,
        base_asset: str,
        quote_asset: str,
    ) -> BasicTradingIndicator | None:
        raise NotImplementedError
