# collect.py

import time
from abc import ABCMeta, abstractmethod
import datetime as dt
import threading
from typing import (
    Optional, Union, Dict, Iterable,
    Any, Protocol, List, Type
)

import pandas as pd
import ccxt.pro as ccxtpro
import ccxt

from represent import BaseModel, Modifiers

from auto_screener.dataset import OHLCV_COLUMNS, DATE_TIME
from auto_screener.hints import Number
from auto_screener.base import terminate_thread
from auto_screener.tickers import parts_to_ticker

__all__ = [
    "wait_for_update",
    "wait_for_initialization",
    "WaitingState",
    "AutoDataCollector",
    "is_valid_ticker",
    "validate_ticker",
    "collect_exchanges",
    "collect_assets",
    "collect_mutual_assets",
    "collect_tickers",
    "collect_mutual_tickers",
    "configure_exchange",
    "is_valid_source",
    "ohlcv_to_dataset",
    "find_screeners",
    "wait_for_dynamic_update",
    "wait_for_dynamic_initialization"
]

class WaitingState(BaseModel):
    """A class to represent the waiting state of screener objects."""

    modifiers = Modifiers(excluded=["screeners"])

    def __init__(
            self, screeners: Iterable,
            delay: Number,
            count: int,
            canceled: bool,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param screeners: The screener objects.
        :param delay: The waiting delay.
        :param count: The iterations count.
        :param canceled: The value for the waiting being canceled.
        :param cancel: The time to cancel the waiting.
        """

        self.screeners: Iterable[AutoDataCollector] = screeners

        self.delay = delay
        self.cancel = cancel
        self.count = count

        self.canceled = canceled

        self.time = dt.timedelta(seconds=self.delay * self.count)
    # end __init__
# end WaitingState

class AutoDataCollector(Protocol, metaclass=ABCMeta):
    """A class to represent an abstract parent class of data collectors."""

    market: pd.DataFrame

    ticker: str
    source: str

    screening_process: Optional[threading.Thread]
    timeout_process: Optional[threading.Thread]

    running: bool
    block: bool

    cancel: Union[Number, dt.timedelta, dt.datetime]

    TICKERS: Dict[str, List[str]] = {
        exchange: [] for exchange in ccxtpro.exchanges
    }
    EXCHANGES: Dict[str, ccxt.Exchange] = {}

    def validate_ticker(self, ticker: Any) -> str:
        """
        Validates the ticker value.

        :param ticker: The name of the ticker.

        :return: The validates ticker.
        """

        if not hasattr(self, "source"):
            raise AttributeError(
                f"Source attribute must be defined before "
                f"attempting to validate the ticker attribute."
            )
        # end if

        return validate_ticker(self.source, ticker, screener=self)
    # end validate_ticker

    def wait_for_initialization(
            self,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            once: Optional[bool] = False,
            stop: Optional[Union[bool, int]] = False,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState:
        """
        Waits for all the screeners to update.

        :param delay: The delay for the waiting.
        :param once: The value to get data only once.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return wait_for_initialization(
            self, delay=delay, once=once,
            stop=stop, cancel=cancel or self.cancel
        )
    # end wait_for_initialization

    def wait_for_update(
            self,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            once: Optional[bool] = False,
            stop: Optional[Union[bool, int]] = False,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState:
        """
        Waits for all the screeners to update.

        :param delay: The delay for the waiting.
        :param once: The value to get data only once.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return wait_for_update(
            self, delay=delay, once=once,
            stop=stop, cancel=cancel or self.cancel
        )
    # end wait_for_update

    def blocking(self) -> bool:
        """
        returns the value of the process being blocked.

        :return: The value.
        """

        return self.block
    # end blocking

    @abstractmethod
    def run_loop(self) -> None:
        """Runs the process of the price screening."""

    def run(
            self,
            wait: Optional[Union[bool, Number, dt.timedelta, dt.datetime]] = False,
            block: Optional[bool] = False,
            timeout: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> threading.Thread:
        """
        Runs the process of the price screening.

        :param wait: The value to wait after starting to run the process.
        :param block: The value to block the execution.
        :param timeout: The valur to add a timeout to the process.
        """

        self.screening_process = threading.Thread(target=self.run_loop)

        self.screening_process.start()

        if timeout:
            self.timeout(timeout)
        # end if

        if block:
            self.block = block

            while self.blocking():
                pass
            # end while
        # end if

        if isinstance(wait, dt.datetime):
            wait = wait - dt.datetime.now()
        # end if

        if isinstance(wait, dt.timedelta):
            wait = wait.total_seconds()
        # end if

        if isinstance(wait, bool) and wait:
            self.wait_for_initialization()

        elif isinstance(wait, (int, float)):
            time.sleep(wait)
        # end if

        return self.screening_process
    # end run

    def timeout(
            self, duration: Union[Number, dt.timedelta, dt.datetime]
    ) -> threading.Thread:
        """
        Runs a timeout for the process.

        :param duration: The duration of the timeout.

        :return: The timeout process.
        """

        if isinstance(duration, dt.datetime):
            duration = duration - dt.datetime.now()
        # end if

        if isinstance(duration, dt.timedelta):
            duration = duration.total_seconds()
        # end if

        self.timeout_process = threading.Thread(
            target=lambda: (time.sleep(duration), self.terminate())
        )

        self.timeout_process.start()

        return self.timeout_process
    # end timeout

    def terminate(self) -> None:
        """Stops the trading process."""

        self.stop()
    # end terminate

    def stop(self) -> None:
        """Stops the screening process."""

        self.running = False

        terminate_thread(self.screening_process)
    # end stop
# end AutoDataCollector

def is_valid_ticker(
        source: str,
        ticker: str,
        screener: Optional[
            Union[AutoDataCollector, Type[AutoDataCollector]]
        ] = None
) -> bool:
    """
    Returns a value for the ticker being valid for the source exchange.

    :param source: The name of the exchange platform.
    :param ticker: The ticker of the assets.
    :param screener: The screener object for the exchanges.

    :return: The validation-value.
    """

    return ticker in (screener or AutoDataCollector).TICKERS[source]
# end is_valid_ticker

def validate_ticker(
        source: str,
        ticker: str,
        screener: Optional[
            Union[AutoDataCollector, Type[AutoDataCollector]]
        ] = None
) -> str:
    """
    Validates the ticker value.

    :param source: The name of the exchange platform.
    :param ticker: The name of the ticker.
    :param screener: The screener object for the exchanges.

    :return: The validates ticker.
    """

    if not is_valid_ticker(source, ticker, screener=screener):
        raise ValueError(
            f"ticker {ticker} is not a valid "
            f"ticker for the {source} exchange."
        )
    # end if

    return ticker
# end validate_ticker

def wait_for_dynamic_initialization(
        screeners: Iterable[AutoDataCollector],
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the screeners to update.

    :param screeners: The screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    if isinstance(cancel, (int, float)):
        cancel = dt.timedelta(seconds=cancel)
    # end if

    current_time = dt.datetime.now()

    if isinstance(cancel, dt.timedelta):
        cancel = current_time + cancel
    # end if

    if isinstance(delay, dt.timedelta):
        delay = delay.total_seconds()
    # end if

    delay = delay or 0
    count = 0

    while (
        any(len(screener.market) == 0 for screener in screeners) or
        (current_time := dt.datetime.now()) <= cancel
    ):
        count += 1

        if isinstance(delay, (int, float)) and (count > 0):
            time.sleep(delay)
        # end if
    # end while

    if stop and ((stop == count) or once):
        for screener in screeners:
            screener.stop()
        # end for
    # end if

    return WaitingState(
        screeners=screeners, delay=delay, count=count,
        cancel=cancel, canceled=current_time > cancel
    )
# end wait_for_dynamic_initialization

def wait_for_initialization(
        *screeners: AutoDataCollector,
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the screeners to update.

    :param screeners: The screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    return wait_for_dynamic_initialization(
        screeners, delay=delay, once=once,
        stop=stop, cancel=cancel
    )
# end wait_for_initialization

def wait_for_dynamic_update(
        screeners: Iterable[AutoDataCollector],
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the screeners to update.

    :param screeners: The screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    if isinstance(cancel, (int, float)):
        cancel = dt.timedelta(seconds=cancel)
    # end if

    current_time = dt.datetime.now()

    if isinstance(cancel, dt.timedelta):
        cancel = current_time + cancel
    # end if

    if isinstance(delay, dt.timedelta):
        delay = delay.total_seconds()
    # end if

    delay = delay or 0
    count = 0

    if screeners:
        wait_for_dynamic_initialization(
            screeners, delay=delay, once=once
        )

        indexes = [
            screener.market.index[-1]
            for screener in screeners
        ]

        new_indexes = indexes

        length = len(tuple(screeners))

        while (
            any(
                indexes[i] == new_indexes[i]
                for i in range(length)
            ) or
            (current_time := dt.datetime.now()) <= cancel
        ):
            count += 1

            new_indexes = [
                screener.market.index[-1]
                for screener in screeners
            ]

            if isinstance(delay, (int, float)) and (count > 0):
                time.sleep(delay)
            # end if
        # end while

        if stop and ((stop == count) or once):
            for screener in screeners:
                screener.stop()
            # end for
        # end if
    # end if

    return WaitingState(
        screeners=screeners, delay=delay, count=count,
        canceled=current_time > cancel, cancel=cancel
    )
# end wait_for_dynamic_update

def wait_for_update(
        *screeners: AutoDataCollector,
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the screeners to update.

    :param screeners: The screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    return wait_for_dynamic_update(
        screeners, delay=delay, once=once,
        stop=stop, cancel=cancel
    )
# end wait_for_update

def _collect_exchange_assets(
        data: Dict[str, List[str]],
        source: str,
        exchange: ccxt.Exchange,
        quotes: Optional[Iterable[str]] = None
) -> None:
    """
    Collects the tickers from the exchanges.

    :param source: The name of the exchange.
    :param exchange: The exchange object.
    :param data: The data to collect the assets.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    quotes = quotes or []
    assets = []

    # noinspection PyBroadException
    try:
        for value in exchange.load_markets().values():
            if quotes and (value['quote'] not in quotes):
                continue
            # end if

            assets.append(value['base'])
        # end for

        data[source] = list(set(assets))

    except Exception:
        data[source] = []
    # end try
# end _collect_exchange_assets

def _collect_exchange_tickers(
        data: Dict[str, List[str]],
        source: str,
        exchange: ccxt.Exchange,
        quotes: Optional[Iterable[str]] = None
) -> None:
    """
    Collects the tickers from the exchanges.

    :param source: The name of the exchange.
    :param exchange: The exchange object.
    :param data: The data to collect the assets.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    quotes = quotes or []
    tickers = []

    # noinspection PyBroadException
    try:
        for value in exchange.load_markets().values():
            if quotes and (value['quote'] not in quotes):
                continue
            # end if

            tickers.append(
                parts_to_ticker(value['base'], value['quote'])
            )
        # end for

        data[source] = list(set(tickers))

    except Exception:
        data[source] = []
    # end try
# end _collect_exchange_tickers

def collect_assets(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    quotes = quotes or []

    data = {}
    markets = {}

    count = 0

    for source in (exchanges or ccxt.__dict__):
        if source in ccxt.exchanges:
            exchange = getattr(ccxt, source)()

            if not (
                hasattr(exchange, 'fetch_tickers') or
                hasattr(exchange, 'watch_tickers')
            ):
                count -= 1

                continue
            # end if

            markets[source] = exchange
        # end if
    # end for

    for source, exchange in markets.items():
        threading.Thread(
            target=_collect_exchange_assets,
            kwargs=dict(
                source=source, exchange=exchange,
                data=data, quotes=quotes
            )
        ).start()
    # end for

    while (len(markets) - count) > len(data):
        pass
    # end while

    return {key: value for key, value in data.items() if value}
# end collect_tickers

def collect_mutual_assets(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    exchanges = collect_assets(exchanges=exchanges, quotes=quotes)

    assets = {}

    for source in exchanges:
        for asset in exchanges[source]:
            assets[asset] = assets.setdefault(asset, 0) + 1
        # end for
    # end for

    return {
        source: [
            asset for asset in exchanges[source]
            if assets.get(asset, 0) > 1
        ]
        for source in exchanges
    }
# end collect_mutual_assets

def collect_tickers(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    quotes = quotes or []

    data = {}
    markets = {}

    count = 0

    for source in (exchanges or ccxt.__dict__):
        if source in ccxt.exchanges:
            exchange = getattr(ccxt, source)()

            if not (
                hasattr(exchange, 'fetch_tickers') or
                hasattr(exchange, 'watch_tickers')
            ):
                count -= 1

                continue
            # end if

            markets[source] = exchange
        # end if
    # end for

    for source, exchange in markets.items():
        threading.Thread(
            target=_collect_exchange_tickers,
            kwargs=dict(
                source=source, exchange=exchange,
                data=data, quotes=quotes
            )
        ).start()
    # end for

    while (len(markets) - count) > len(data):
        pass
    # end while

    return {key: value for key, value in data.items() if value}
# end collect_tickers

def collect_mutual_tickers(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.

    :return: The data of the exchanges.
    """

    exchanges = collect_tickers(exchanges=exchanges, quotes=quotes)

    tickers = {}

    for source in exchanges:
        for ticker in exchanges[source]:
            tickers[ticker] = tickers.setdefault(ticker, 0) + 1
        # end for
    # end for

    return {
        source: [
            ticker for ticker in exchanges[source]
            if tickers.get(ticker, 0) > 1
        ]
        for source in exchanges
    }
# end collect_mutual_tickers

def collect_exchanges(
        currencies: Dict[str, List[str]],
        pairs: Dict[str, List[str]],
        excluded: Optional[Dict[str, Iterable[str]]] = None,
) -> Dict[str, List[str]]:
    """
    Collects the exchanges.

    :param pairs: The data of currencies and their traded quote assets.
    :param currencies: The data of exchanges and their traded currencies.
    :param excluded: The data of excluded pairs for each exchange.

    :return: The data of exchanges and their tickers.
    """

    exchanges: Dict[str, List[str]] = {}

    for platform, currencies in currencies.items():
        exchanges[platform] = []

        for currency in currencies:
            for asset in pairs[currency]:
                if (
                    parts_to_ticker(asset, currency) in
                    excluded.get(platform, [])
                ):
                    continue
                # end if

                exchanges[platform].append(
                    parts_to_ticker(asset, currency)
                )
            # end for
        # end for
    # end for

    return exchanges
# end collect_exchanges

def ohlcv_to_dataset(data: Iterable[Iterable]) -> pd.DataFrame:
    """
    Adjusts the dataset to an asset Open, High, Low, Close, Bids, Asks, Volume dataset.

    :param data: The data to adjust.

    :return: The asset dataset.
    """

    data = pd.DataFrame(data)

    index_column_name = list(data.columns)[0]

    data.index = pd.to_datetime(data[index_column_name], unit="ms")
    del data[index_column_name]
    data.index.name = DATE_TIME
    data.columns = list(OHLCV_COLUMNS)

    return data
# end ohlcv_to_dataset

def is_valid_source(
        source: str,
        screener: Optional[
            Union[AutoDataCollector, Type[AutoDataCollector]]
        ] = None
) -> bool:
    """
    checks of the source os a valid exchange name.

    :param source: The source name to validate.
    :param screener: The screener object for the exchanges.

    :return: The validation value.
    """

    return source in (screener or AutoDataCollector).TICKERS
# end is_valid_source

def configure_exchange(
        source: str,
        pro: Optional[bool] = True,
        screener: Optional[
            Union[AutoDataCollector, Type[AutoDataCollector]]
        ] = None,
        options: Optional[Dict[str, Any]] = None
):
    """
    Validates the exchange source value.

    :param source: The name of the exchange platform.
    :param screener: The screener object for the exchanges.
    :param pro: The value for the pro interface.
    :param options: The ccxt options.

    :return: The validates source.
    """

    screener = screener or AutoDataCollector

    if source not in screener.EXCHANGES:
        try:
            exchange = getattr(
                (ccxtpro if pro else ccxt), source
            )(options)

        except AttributeError:
            raise ValueError(f"Unrecognized exchange name: {source}.")
        # end try

        if not (
            hasattr(exchange, "watch_tickers") or
            hasattr(exchange, "fetch_tickers")
        ):
            raise ValueError(f"Cannot extract data from {source}.")
        # end if

        if not screener.TICKERS.setdefault(source, []):
            try:
                screener.TICKERS[source] = list(
                    getattr(ccxt, source)().load_markets().keys()
                )

            except Exception as e:
                raise ValueError(
                    f"Cannot fetch tickers from {source}. {e}"
                )
            # end try
        # end if

        screener.EXCHANGES[source] = exchange
    # end if

    return screener.EXCHANGES[source]
# end configure_exchange

def find_screeners(
        ticker: str, source: str, screeners: Iterable[AutoDataCollector]
) -> List[AutoDataCollector]:
    """
    Finds the screeners with the given source exchange and ticker.

    :param ticker: The ticker of the screener.
    :param source: The exchange name of the screener.
    :param screeners: The screeners to search in.

    :return: A list of the matching screeners.
    """

    found = []

    for screener in screeners:
        if (screener.source == source) and (screener.ticker == ticker):
            found.append(screener)
        # end if
    # end for

    return found
# end find_screeners