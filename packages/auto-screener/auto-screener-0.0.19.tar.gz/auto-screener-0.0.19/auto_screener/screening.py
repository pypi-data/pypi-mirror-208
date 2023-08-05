# screening.py

import os
import time
import asyncio
import warnings
import datetime as dt
import threading
from typing import (
    Optional, Union, Dict, Iterable, Any, List, Set
)

import pandas as pd
import numpy as np
import ccxt
import ccxt.pro as ccxtpro

from represent import BaseModel, Modifiers

from auto_screener.hints import Number
from auto_screener.dataset import (
    OPEN, HIGH, LOW, CLOSE, VOLUME, BIDS,
    ASKS, row_to_dataset, DATE_TIME
)
from auto_screener.base import terminate_thread
from auto_screener.interval import interval_to_total_time
from auto_screener.dataset import save_dataset, load_dataset
from auto_screener.collect import (
    AutoDataCollector, ohlcv_to_dataset,
    wait_for_update, WaitingState, configure_exchange,
    wait_for_dynamic_update, wait_for_dynamic_initialization
)

__all__ = [
    "AutoDataset",
    "AutoScreener",
    "MultiScreener",
    "ScreenerSignature",
    "live_screeners"
]

class AutoScreener(BaseModel, AutoDataCollector):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - ticker:
        The ticker symbol of an asset to screen.

    - source:
        The name of the exchange platform to screen data from.

    - delay:
        The delay to wait between each data fetching.

    - pro:
        The value to use the pro interface.

    - options:
        The ccxt options for the backend screening process.

    - cencel:
        The time to cancel screening process after no new data is fetched.

    >>> from auto_screener.screening import AutoScreener
    >>> from auto_screener.collect wait_for_initialization
    >>>
    >>> screener = AutoScreener(
    >>>     ticker="BTC/USD", source="binance"
    >>> )
    >>>
    >>> screener.run(wait=True)
    >>>
    >>> while True:
    >>>     print(screener.market.iloc[-1])
    >>>
    >>>     wait_for_update(screener, delay=1)
    """

    modifiers = Modifiers(
        excluded=[
            "market", "exchange", "screening_process",
            "task", 'timeout_process'
        ]
    )

    ASKS = ASKS
    BIDS = BIDS

    DELAY = 0.0
    CANCEL = 60

    COLUMNS = (
        OPEN, HIGH, LOW, CLOSE,
        ASKS, BIDS, VOLUME
    )

    def __init__(
            self,
            ticker: str,
            source: str,
            pro: Optional[bool] = True,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            options: Optional[Dict[str, Any]] = None,
            cancel: Optional[Union[int, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param delay: The delay for the process.
        :param pro: The value for the pro interface.
        :param options: The ccxt options.
        """

        self.options = options or {}

        self.exchange = configure_exchange(
            source=source, pro=pro, options=self.options
        )

        self.delay = delay or self.DELAY
        self.cancel = cancel or self.CANCEL

        self.pro = pro

        self.source = source

        self.ticker = self.validate_ticker(ticker=ticker)

        self.running = False
        self.block = False

        self.market = pd.DataFrame(
            {column: [] for column in self.COLUMNS}, index=[]
        )

        self.market.index.name = DATE_TIME

        self.screening_process = None
        self.timeout_process = None

        self.task = None
    # end __init__

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the data of the object.

        :return: The state of the object.
        """

        data = self.__dict__.copy()

        data["task"] = None
        data["screening_process"] = None
        data["timeout_process"] = False
        data["exchange"] = None

        return data
    # end __getstate__

    async def async_get_market(self) -> Dict[str, Number]:
        """
        Gets the market data.

        :return: The bids and asks.
        """

        if hasattr(self.exchange, "fetch_tickers"):
            method = self.exchange.fetch_tickers

        elif hasattr(self.exchange, "watch_tickers"):
            method = self.exchange.watch_tickers

        else:
            raise AttributeError(
                f"Exchange attribute {self.exchange} of "
                f"{self} must has at least one of the "
                f"methods 'fetch_tickers', or 'watch_tickers'."
            )
        # end if

        if isinstance(self.exchange, getattr(ccxtpro, self.source)):
            data = await method(symbols=[self.ticker])

        elif isinstance(self.exchange, getattr(ccxt, self.source)):
            data = method(symbols=[self.ticker])

        else:
            raise TypeError(
                f"Exchange object {self.exchange} of "
                f"{self} must be from ccxt."
            )
        # end if

        ticker = list(data.keys())[0]

        data[ticker][VOLUME.lower()] = data[ticker]["quoteVolume"]
        data[ticker][self.ASKS.lower()] = data[ticker]["ask"]
        data[ticker][self.BIDS.lower()] = data[ticker]["bid"]

        return {
            key: data[ticker][key.lower()] for key in
            self.COLUMNS
        }
    # end async_get_market

    async def get_market(self) -> Dict[str, Number]:
        """
        Gets the market data.

        :return: The bids and asks.
        """

        task = self.async_get_market()

        try:
            loop = asyncio.get_event_loop()

            self.task = loop.create_task(task)

            return await self.task

        except RuntimeError:
            return asyncio.run(task)
        # end try
    # end get_market

    async def async_run_loop(self) -> None:
        """Runs the processes of price screening."""

        self.running = True

        delay = self.delay

        if isinstance(delay, dt.timedelta):
            delay = delay.total_seconds()
        # end if

        while self.running:
            start = time.time()

            try:
                data = await self.async_get_market()

            except Exception as e:
                self.terminate()

                raise RuntimeError(
                    f"Could not complete task. {str(e)}"
                ) from e
            # end try

            new_data = pd.DataFrame(
                data, index=[dt.datetime.now()]
            )
            new_data.index.name = DATE_TIME

            self.market = pd.concat([self.market, new_data])
            self.market.index.name = DATE_TIME

            end = time.time()

            if delay:
                time.sleep(max([delay - (end - start), 0]))
            # end if
        # end while
    # end async_run

    async def async_run(self) -> None:
        """Runs the processes of price screening."""

        task = self.async_run_loop()

        try:
            loop = asyncio.get_event_loop()

            self.task = loop.create_task(task)

            await self.task

        except RuntimeError:
            asyncio.run(task)
        # end try
    # end async_run

    def run_loop(self) -> None:
        """Runs the process of the price screening."""

        asyncio.run(self.async_run())
    # end run_loop

    def stop(self) -> None:
        """Stops the screening process."""

        super().stop()

        if self.task is not None:
            self.task.cancel()
        # end if
    # end stop

    def terminate(self) -> None:
        """Stops the trading process."""

        super().terminate()
    # end terminate
# end Screener

class ScreenerSignature(BaseModel):
    """
    A class to represent a screener signature.

    Parameters:

    - ticker:
        The ticker symbol of an asset to screen.

    - source:
        The name of the exchange platform to screen data from.

    - delay:
        The delay to wait between each data fetching.

    - pro:
        The value to use the pro interface.
    """

    def __init__(
            self,
            ticker: str,
            source: str,
            pro: bool,
            delay: Union[Number, dt.timedelta]
    ) -> None:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param delay: The delay for the process.
        :param pro: The value for the pro interface.
        """

        self.ticker = ticker
        self.source = source

        self.pro = pro

        self.delay = delay
    # end __init__
# end ScreenerSignature

class AutoDataset(BaseModel, AutoDataCollector):
    """
    A class to represent a live asset data builder.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    You can also use it to build real time datasets of Open
    High Low Close Volume, with Bids and Asks.

    Parameters:

    - ticker:
        The ticker symbol of an asset to screen.

    - source:
        The name of the exchange platform to screen data from.

    - interval:
        The interval for the time between data points in the dataset.

    - delay:
        The delay to wait between each data fetching.

    - screener:
        The screener object to connect to for creating the dataset.

    - length:
        An initial dataset length to start with.

    - pro:
        The value to use the pro interface.

    - options:
        The ccxt options for the backend screening process.

    - cencel:
        The time to cancel screening process after no new data is fetched.

    >>> from auto_screener.screening import AutoDataset
    >>> from auto_screener.collect wait_for_initialization
    >>> from auto_screener.interval import interval_to_total_time
    >>>
    >>> interval = "1m"
    >>>
    >>> dataset = AutoDataset(
    >>>     ticker="BTC/USD", source="binance", interval=interval
    >>> )
    >>>
    >>> dataset.run(wait=True)
    >>>
    >>> print(dataset.market.iloc[-1].splitlines()[0])
    >>>
    >>> while True:
    >>>     print(dataset.market.iloc[-1].splitlines()[-1])
    >>>
    >>>     wait_for_update(dataset, delay=interval_to_total_time(interval))
    """

    modifiers = Modifiers(
        excluded=[
            "timeout_process", 'market', 'built',
            'exchange', 'screening_process', "delay"
        ]
    )

    screeners: Dict[ScreenerSignature, AutoScreener] = {}

    EXCHANGES = AutoScreener.EXCHANGES
    COLUMNS = AutoScreener.COLUMNS
    TICKERS = AutoScreener.TICKERS

    DELAY = 1
    CANCEL = 60

    def __init__(
            self,
            ticker: str,
            source: str,
            interval: str,
            pro: Optional[bool] = True,
            data: Optional[pd.DataFrame] = None,
            length: Optional[Union[bool, int]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            screener: Optional[AutoScreener] = None,
            options: Optional[Dict[str, Any]] = None,
            cancel: Optional[Union[int, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param interval: The interval for the data.
        :param data: The base dataset of the asset to add to.
        :param length: The length of the base dataset.
        :param delay: The delay for the process.
        :param screener: The screener object for the dataset.
        :param pro: The value for the pro interface.
        :param options: The ccxt options.
        """

        self.options = options or {}

        self.source = source

        self.interval = interval
        self.ticker = ticker

        self.delay = delay or self.DELAY
        self.cancel = cancel or self.CANCEL

        self.built = False

        self.pro = pro

        self.signature = ScreenerSignature(
            ticker=self.ticker, source=self.source,
            delay=self.delay, pro=self.pro
        )

        if self.signature not in self.screeners:
            if screener is None:
                self.built = True

                screener = AutoScreener(
                    ticker=self.ticker, source=self.source,
                    delay=self.delay, pro=self.pro,
                    options=self.options
                )
            # end if

            self.screeners[self.signature] = screener
        # end if

        self.screener = self.screeners[self.signature]

        self.market = self.validate_data(data, length=length)

        ccxt.binance()

        self.exchange = getattr(ccxt, self.source)(self.options)

        self.screening_process = None
        self.timeout_process = None

        self.running = False
        self.block = False
    # end __init__

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the data of the object.

        :return: The state of the object.
        """

        data = self.__dict__.copy()

        data["exchange"] = None

        return data
    # end __getstate__

    def __setstate__(self, state: Dict[str, Any]) -> Any:
        """
        Sets the state of the object.

        :param state: The state to set to the object.
        """

        self.__dict__.update(state)

        self.exchange = getattr(ccxt, self.source)()
    # end __setstate__

    def validate_data(self, data: Any, length: Optional[int]) -> pd.DataFrame:
        """
        Validates the asset data value.

        :param data: The asset data.
        :param length: The length of the data to add.

        :return: The validates source.
        """

        if not all(
            hasattr(self, name) for name in ["source", "interval"]
        ):
            raise AttributeError(
                "Source and interval attributes must be defined "
                "before attempting to validate the data parameter data."
            )
        # end if

        if (
            (data is None) and
            (
                (length is None) or
                (length == 0) or
                (length is False) or
                (
                    isinstance(length, int) and
                    not (0 < length <= 500)
                )
            )
        ):
            data = pd.DataFrame(
                {column: [] for column in self.COLUMNS},
                index=[]
            )

        elif (data is None) and (isinstance(length, int)):
            if 0 < length <= 500:
                data = self.data_to_dataset(
                    self.exchange.fetch_ohlcv(
                        symbol=self.ticker,
                        timeframe=self.interval,
                        limit=length
                    )
                )

            else:
                raise ValueError(
                    f"Length must be a positive int between "
                    f"1 and 500 when data is not defined, "
                    f"not: {length}."
                )
            # end if
        # end if

        return data
    # end validate_data

    def data_to_dataset(self, data: Iterable[Iterable]) -> pd.DataFrame:
        """
        Adjusts the dataset to an asset Open, High, Low, Close, Bids, Asks, Volume dataset.

        :param data: The data to adjust.

        :return: The asset dataset.
        """

        data = ohlcv_to_dataset(data=data)

        if len(self.screener.market) == 0:
            asks = [np.nan] * len(data)
            bids = [np.nan] * len(data)

        else:
            asks = (
                self.screener.market[AutoScreener.ASKS].iloc
                [-len(data):].values[:]
            )
            bids = (
                self.screener.market[AutoScreener.BIDS].iloc
                [-len(data):].values[:]
            )
        # end if

        data[AutoScreener.ASKS].values[:] = asks
        data[AutoScreener.BIDS].values[:] = bids

        return data[list(self.COLUMNS)]
    # end data_to_dataset

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

        if not self.screener.running:
            self.screener.run(wait=True, block=False, timeout=timeout)
        # end if

        return super().run(wait=wait, block=block, timeout=timeout)
    # end run

    def run_loop(self) -> None:
        """Runs the process of the price screening."""

        self.running = True

        delay = interval_to_total_time(self.interval).seconds

        while self.running:
            start = time.time()

            data = row_to_dataset(self.screener.market, index=-1)

            # noinspection PyBroadException
            try:
                prices = self.validate_data(data=None, length=1)
                prices[AutoScreener.BIDS].values[:] = (
                    data[AutoScreener.BIDS].values[:]
                )
                prices[AutoScreener.ASKS].values[:] = (
                    data[AutoScreener.ASKS].values[:]
                )
                data = prices

            except Exception as e:
                warnings.warn(str(e))
            # end try

            end = time.time()

            self.market = pd.concat([self.market, data])
            self.market = self.market[
                ~self.market.index.duplicated(keep='first')
            ]

            time.sleep(max([delay - (end - start), 0]))
        # end while
    # end run_loop

    def terminate(self) -> None:
        """Stops the trading process."""

        super().terminate()

        if self.built:
            self.screener.terminate()
        # end if
    # end terminate

    def stop(self) -> None:
        """Stops the screening process."""

        super().stop()

        if self.built:
            self.screener.stop()
        # end if
    # end stop
# end LiveAssetData

Screener = Union[AutoScreener, AutoDataset]

class MultiScreener(BaseModel):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - exchanges:
        The data of exchanges and their tickers to screen.

    - interval:
        The interval for the time between data points in the dataset.

    - delay:
        The delay to wait between each data fetching.

    - length:
        An initial dataset length to start with.

    - locaion:
        The saving location for the saved data of the screener.

    - pro:
        The value to use the pro interface.

    - options:
        The ccxt options for the backend screening process.

    - cencel:
        The time to cancel screening process after no new data is fetched.

    >>> from auto_screener.screening import MultiScreener
    >>> from auto_screener.collect wait_for_initialization
    >>>
    >>> screener = MultiScreener(
    >>>     exchanges={
    >>>         "binance": ["BTC/USDT", "AAVE/EUR"],
    >>>         "bittrex": ["GRT/USD", "BTC/USD"]
    >>>     }
    >>> )
    >>>
    >>> screener.run(wait=True)
    >>>
    >>> while True:
    >>>     screener.wait_for_update(delay=1)
    """

    modifiers = Modifiers(
        excluded=[
            "exchange", "screening_process",
            "timeout_process", "screeners"
        ]
    )

    LOCATION = "datasets"
    INTERVAL = "1m"

    DELAY = 1
    CANCEL = 60

    PRO = False

    OPTIONS = {}

    def __init__(
            self,
            exchanges: Dict[str, Iterable[str]],
            delay: Optional[Union[Number, dt.timedelta]] = None,
            interval: Optional[Union[bool, str]] = None,
            length: Optional[Union[int, bool]] = None,
            location: Optional[str] = None,
            pro: Optional[bool] = None,
            options: Optional[Dict[str, Any]] = None,
            cancel: Optional[Union[int, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param interval: The interval of the data to load.
        :param exchanges: The data of exchanges and their tickers.
        :param pro: The value to use the pro interface.
        :param location: The saving location for the data.
        :param delay: The delay between each data fetching request.
        :param length: The length of the data to get in each request.
        :param options: The ccxt options.
        :param cancel: The time it takes to cancel a non-updating screener.
        """

        if isinstance(interval, bool) and interval:
            interval = self.INTERVAL

        elif isinstance(interval, bool):
            interval = None
        # end if

        self.options = options or self.OPTIONS

        self.interval = interval
        self.location = location or self.LOCATION

        self.delay = delay or self.DELAY
        self.cancel = cancel or self.CANCEL
        self.length = length

        self.pro = pro or self.PRO

        self.exchanges = self.validate_exchanges(exchanges)

        self.running = False
        self.block = False
        self.saving = False

        self.market: Dict[str, Dict[str, Optional[Screener]]] = {}
        self.invalid: Dict[str, List[str]] = {}
        self.screeners: List[Screener] = []
        self.stopped: List[Screener] = []
        self.loaded: Set[Screener] = set()

        self.saving_process = None
        self.timeout_process = None
    # end Screener

    @staticmethod
    def validate_exchanges(data: Any) -> Dict[str, List[str]]:
        """
        Validates the data.

        :param data: The data to validate.

        :return: The valid data.
        """

        if data is None:
            return {}
        # end if

        try:
            if not isinstance(data, dict):
                raise ValueError
            # end if

            new_data = {}

            for key, values in data.items():
                values = list(values)

                if not (
                    isinstance(key, str) and
                    all(isinstance(value, str) for value in values)
                ):
                    raise ValueError
                # end if

                new_data[key] = values
            # end for

        except (TypeError, ValueError):
            raise ValueError(
                f"Exchanges data must be a dictionary of "
                f"exchange names as keys and iterables of "
                f"ticker names as values, not {data}."
            )
        # end try

        return new_data
    # end validate_data

    @staticmethod
    def dataset_path(
            screener: Screener, location: Optional[str] = None
    ) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param screener: The screener object.
        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        return (location + "/" if isinstance(location, str) else "") + (
            f"{screener.source}/{screener.ticker.replace('/', '-')}.csv"
        )
    # end dataset_path

    def create_screener(
            self,
            container: Dict[str, Optional[Screener]],
            ticker: str,
            source: str
    ) -> None:
        """
        Creates the screener and inserts it into the container.

        :param container: The container to contain the new screener.
        :param ticker: The ticker of the screener.
        :param source: The source of the data.
        """

        try:
            if isinstance(self.interval, str):
                container[ticker] = AutoDataset(
                    ticker=ticker, source=source, options=self.options,
                    interval=self.interval, pro=self.pro, delay=self.delay
                )

            else:
                container[ticker] = AutoScreener(
                    ticker=ticker, source=source, options=self.options,
                    pro=self.pro, delay=self.delay
                )
            # end if

        except ValueError:
            container[ticker] = None

            self.invalid.setdefault(source, []).append(ticker)
        # end try
    # end create_screener

    def configure_screener_dataset(
            self,
            screener: Screener,
            location: Optional[str] = None,
            length: Optional[int] = None
    ) -> None:
        """
        Configures the dataset of the screener.

        :param screener: The screener object to configure the dataset for.
        :param location: The saving or loading path for the dataset.
        :param length: The length of the dataset to fetch.
        """

        path = self.dataset_path(screener=screener, location=location)

        if os.path.exists(path):
            try:
                self.load_dataset(screener=screener)

            except Exception as e:
                warnings.warn(str(e))
            # end try

        else:
            if isinstance(screener, AutoDataset):
                screener.market = screener.validate_data(
                    data=None, length=length
                )
            # end if

            if len(screener.market) > 0:
                self.save_dataset(screener=screener)
            # end if
        # end if
    # end configure_screener_dataset

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

        return wait_for_dynamic_initialization(
            self.screeners, delay=delay, once=once,
            stop=stop, cancel=cancel
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

        return wait_for_dynamic_update(
            self.screeners, delay=delay, once=once,
            stop=stop, cancel=cancel
        )
    # end wait_for_update

    def initialize_screeners(self) -> None:
        """Initializes the screeners."""

        self.market.clear()

        for exchange, tickers in self.exchanges.items():
            self.market[exchange] = {}

            for ticker in tickers:
                threading.Thread(
                    target=self.create_screener,
                    kwargs=dict(
                        container=self.market[exchange],
                        ticker=ticker, source=exchange
                    )
                ).start()
            # end for
        # end for

        while (
            sum(len(screeners) for screeners in self.market.values()) <
            sum(len(tickers) for tickers in self.exchanges.values())
        ):
            time.sleep(3)
        # end while

        self.screeners.clear()

        for exchange in self.market.values():
            for ticker, screener in exchange.copy().items():
                if isinstance(screener, (AutoScreener, AutoDataset)):
                    self.screeners.append(screener)

                else:
                    exchange.pop(ticker)
                # end if
            # end for
        # end for
    # end initialize_screeners

    def prepare_screeners(self) -> None:
        """Initializes the screeners."""

        if not (self.market and self.screeners):
            self.initialize_screeners()
        # end if

        for screener in self.screeners:
            threading.Thread(
                target=self.configure_screener_dataset,
                kwargs=dict(
                    screener=screener,
                    location=self.location,
                    length=self.length
                )
            ).start()
        # end for
    # end prepare_screeners

    def start_screeners(
            self,
            wait: Optional[Union[bool, Number, dt.timedelta, dt.datetime]] = False,
            timeout: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> None:
        """
        Runs the data collection.

        :param timeout: The valur to add a timeout to the process.
        :param wait: The value to wait after starting to run the process.
        """

        self.prepare_screeners()

        for screener in self.screeners:
            threading.Thread(
                target=screener.run,
                kwargs=dict(
                    timeout=timeout, wait=False, block=False
                )
            ).start()
        # end for

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
    # end start_screeners

    def stop(self) -> None:
        """Stops the screening process."""

        self.saving = False

        terminate_thread(self.saving_process)
    # end stop

    def terminate(self) -> None:
        """Stops the screening process."""

        self.running = False

        self.stop()

        for screener in self.screeners:
            screener.terminate()
        # end for
    # end terminate

    def blocking(self) -> bool:
        """
        returns the value of the process being blocked.

        :return: The value.
        """

        return self.block
    # end blocking

    def save_dataset(self, screener: Screener) -> None:
        """
        Saves the data of the screener.

        :param screener: The screener object to save its data.
        """

        save_dataset(
            dataset=screener.market,
            path=self.dataset_path(
                screener=screener, location=self.location
            )
        )

        if screener in self.loaded:
            self.loaded.remove(screener)
        # end if
    # end save_dataset

    def load_dataset(self, screener: Screener) -> None:
        """
        Saves the data of the screener.

        :param screener: The screener object to save its data.
        """

        screener.market = load_dataset(
            path=self.dataset_path(
                screener=screener, location=self.location
            )
        )

        self.loaded.add(screener)
    # end save_dataset

    def handle(
            self,
            screener: Screener,
            cancel: Optional[Union[int, dt.timedelta]] = None
    ) -> None:
        """
        Handles the screener during the screening loop.

        :param screener: The screener object.
        :param cancel: The time it takes to cancel a non-updating screener.
        """

        if cancel is None:
            cancel = self.cancel
        # end if

        if len(screener.market) == 0:
            return
        # end if

        if isinstance(cancel, dt.timedelta):
            cancel = cancel.total_seconds()
        # end if

        cancel += (
            interval_to_total_time(screener.interval)
            if isinstance(screener, AutoDataset) else 0
        )

        if (
            (screener not in self.loaded) and
            (dt.datetime.now() - screener.market.index[-1]).seconds >= cancel
        ):
            screener.terminate()

            self.stopped.append(screener)
            self.screeners.remove(screener)

        else:
            self.save_dataset(screener=screener)
        # end if
    # end handle

    def run_loop(self) -> None:
        """Runs the process of the price screening."""

        self.running = True

        while self.running:
            for screener in self.screeners.copy():
                self.handle(screener=screener)
            # end for

            delay = self.delay

            if isinstance(self.delay, dt.timedelta):
                delay = delay.total_seconds()
            # end if

            time.sleep(delay or 1)
        # end while
    # end run_loop

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
            target=lambda: (time.sleep(duration), self.stop())
        )

        self.timeout_process.start()

        return self.timeout_process
    # end timeout

    def run(
            self,
            save: Optional[bool] = True,
            block: Optional[bool] = False,
            wait: Optional[Union[bool, Number, dt.timedelta, dt.datetime]] = False,
            timeout: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> Optional[threading.Thread]:
        """
        Runs the process of the price screening.

        :param save: The value to save the data.
        :param block: The value to block the execution.
        :param timeout: The valur to add a timeout to the process.
        :param wait: The value to wait after starting to run the process.
        """

        self.start_screeners(timeout=timeout, wait=wait)

        if save:
            self.saving = True

            self.saving_process = threading.Thread(
                target=self.run_loop
            )

            self.saving_process.start()
        # end if

        if timeout:
            self.timeout(timeout)
        # end if

        if block:
            self.block = block

            while self.blocking() and self.running:
                pass
            # end while
        # end if

        if save:
            return self.saving_process
        # end if
    # end run
# end Screener

def live_screeners(
        screeners: Iterable[Union[Screener, MultiScreener]]
) -> List[Union[Screener, MultiScreener]]:
    """
    Returns a list of all the live screeners.

    :param screeners: The screeners to search from.

    :return: A list the live screeners.
    """

    return [
        screener for screener in screeners
        if (
            screener.running and (
                isinstance(screener, MultiScreener) or
                len(screener.market) > 0
            )
        )
    ]
# end live_screeners