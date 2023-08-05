# tickers.py

from typing import (
    Optional, Tuple, Dict,
    Any, List, Iterable, Union
)

from represent import BaseModel, Modifiers

__all__ = [
    "Pair",
    "ticker_to_pair",
    "ticker_to_parts",
    "pair_to_ticker",
    "parts_to_ticker",
    "reverse_ticker",
    "reverse_pair",
    "adjust_ticker",
    "parts_to_pair",
    "pair_to_parts",
    "tickers_to_parts",
    "parts_to_ticker_parts",
    "parts_to_ticker_parts",
    "assets_to_tickers",
    "parts_to_tickers",
    "Separator"
]

class Separator:
    """A class to contain the separator value."""

    value = "/"
# end Separator

class Pair(BaseModel):
    """
    A class to represent a trading pair.

    This object represents a pair of assets that can be traded.

    attributes:

    - base:
        The asset to buy or sell.

    - quote:
        The asset to use to buy or sell.

    >>> from auto_screener.tickers import Pair
    >>>
    >>> pair = Pair("BTC", "USD")
    """

    modifiers = Modifiers(excluded=["parts"])

    def __init__(self, base: str, quote: str) -> None:
        """
        Defines the class attributes.

        :param base: The base asset of the trading pair.
        :param quote: The target asset of the trading pair.
        """

        self.base = base
        self.quote = quote

        self.parts = (self.base, self.quote)
    # end __init__

    def __getitem__(self, item: Union[slice, int]) -> Union[str, Iterable[str]]:
        """
        Returns the items.

        :param item: The slice item.

        :return: The items in the object to get with the slice.
        """

        data = self.parts[item]

        if isinstance(data, list):
            # noinspection PyTypeChecker
            return type(self)(*data)
        # end if

        return data
    # end __getitem__

    def __len__(self) -> int:
        """
        The length of the assets.

        :return: The length of the assets.
        """

        return len(self.parts)
    # end __len__

    def __iter__(self) -> Iterable[str]:
        """
        Returns the object as an iterable.

        :return: The iterable object.
        """

        yield from self.parts
    # end __iter__

    @staticmethod
    def load(parts: Iterable[str]):
        """
        Creates a pair of assets from the data.

        :param parts: The pair data.

        :return: The pair object.
        """

        if not (
                (len(tuple(parts)) == 2) and
                all(isinstance(part, str) for part in parts)
        ):
            raise ValueError(
                f"Pair data must be an iterable of base asset and "
                f"quote asset of type str, in that order, not {parts}."
            )
        # end if

        return Pair(*parts)
    # end load

    def ticker(self) -> str:
        """
        Gets the tickers of the chain.

        :return: The tickers of the trading chain.
        """

        return pair_to_ticker(self)
    # end tickers

    def json(self) -> Tuple[str, str]:
        """
        Converts the data into a json format.

        :return: The chain of assets.
        """

        return pair_to_parts(self)
    # end json
# end Pair

def pair_to_ticker(pair: Pair, separator: Optional[str] = Separator.value) -> str:
    """
    Converts a pair of assets into a ticker.

    :param pair: The pair of assets.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    return f"{pair.base}{separator}{pair.quote}"
# end pair_to_ticker

def parts_to_ticker(base: str, quote: str, separator: Optional[str] = Separator.value) -> str:
    """
    Converts a pair of assets into a ticker.

    :param base: The base assets.
    :param quote: The quote assets.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    return f"{base}{separator}{quote}"
# end parts_to_ticker

def ticker_to_pair(ticker: str, separator: Optional[str] = Separator.value) -> Pair:
    """
    Converts a pair of assets into a ticker.

    :param ticker: The ticker to convert into a pair object.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    if separator in ticker:
        base = ticker[:ticker.find(separator)]
        quote = ticker[ticker.find(separator) + len(separator):]

    else:
        raise ValueError(
            f"Cannot separate ticker '{ticker}' because "
            f"the given separator '{separator}' is not in the ticker."
        )
    # end if

    return Pair(base=base, quote=quote)
# end ticker_to_pair

def parts_to_pair(base: str, quote: str) -> Pair:
    """
    Converts a pair of assets into a ticker.

    :param base: The base assets.
    :param quote: The quote assets.

    :return: The ticker.
    """

    return Pair(base, quote)
# end parts_to_pair

def ticker_to_parts(ticker: str, separator: Optional[str] = Separator.value) -> Tuple[str, str]:
    """
    Converts a pair of assets into a ticker.

    :param ticker: The ticker to convert into a pair object.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    pair = ticker_to_pair(ticker=ticker, separator=separator)

    return pair.base, pair.quote
# end ticker_to_parts

def reverse_ticker(ticker: str, separator: Optional[str] = Separator.value) -> str:
    """
    Converts a pair of assets into a ticker.

    :param ticker: The ticker to convert into a pair object.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    base, quote = ticker_to_parts(ticker=ticker, separator=separator)

    return parts_to_ticker(base=quote, quote=base)
# end ticker_to_parts

def reverse_pair(pair: Pair, separator: Optional[str] = Separator.value) -> Pair:
    """
    Converts a pair of assets into a ticker.

    :param pair: The pair of assets.
    :param separator: The separator of the assets.

    :return: The ticker.
    """

    return ticker_to_pair(
        reverse_ticker(
            ticker=pair_to_ticker(pair=pair, separator=separator),
            separator=separator
        )
    )
# end ticker_to_parts

def pair_to_parts(pair: Pair) -> Tuple[str, str]:
    """
    Converts a pair of assets into a ticker.

    :param pair: The pair of assets.

    :return: The ticker.
    """

    return pair.base, pair.quote
# end pair_to_parts

def adjust_ticker(ticker: str, separator: Optional[str] = Separator.value) -> str:
    """
    Adjusts the ticker of the asset.

    :param ticker: The ticker of the asset to adjust.
    :param separator: The separator of the assets.

    :return: The adjusted asset ticker.
    """

    ticker = ticker.replace("-", separator)

    if ticker.endswith(f'{separator}USD'):
        ticker = ticker.replace(f"{separator}USD", f"{separator}USDT")
    # end if

    return ticker.replace(separator, "")
# end adjust_ticker

def tickers_to_parts(tickers: Dict[str, Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Collects the bases and quotes of the tickers.

    :param tickers: The tickers to separate.

    :return: The separated bases and quotes.
    """

    quotes = []
    bases = []

    for base in tickers:
        if base not in bases:
            bases.append(base)
        # end if

        for quote in tickers[base]:
            if quote not in quotes:
                quotes.append(quote)
            # end if
        # end for
    # end for

    return bases, quotes
# end tickers_to_parts

def parts_to_ticker_parts(
        bases: Iterable[str],
        quotes: Iterable[str],
        tickers: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Tuple[str, str]]:
    """
    Collects the bases and quotes of the tickers.

    :param bases: The bases to join.
    :param quotes: The quotes to join.
    :param tickers: The tickers to separate.

    :return: The joined tickers.
    """

    pairs = []

    for base in bases:
        for quote in quotes:
            if (
                    ((base, quote) not in pairs) and
                    (
                            (
                                    (tickers is not None) and
                                    (quote in tickers[base])
                            ) or (tickers is None)
                    )
            ):
                pairs.append((base, quote))
            # end if
        # end for
    # end for

    return pairs
# end parts_to_ticker_parts

def parts_to_tickers(
        bases: Iterable[str],
        quotes: Iterable[str],
        tickers: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[str]:
    """
    Collects the bases and quotes of the tickers.

    :param bases: The bases to join.
    :param quotes: The quotes to join.
    :param tickers: The tickers to separate.

    :return: The joined tickers.
    """

    return [
        parts_to_ticker(*parts) for parts in
        (parts_to_ticker_parts(bases, quotes, tickers))
    ]
# end parts_to_tickers

def assets_to_tickers(assets: Iterable[str]) -> List[str]:
    """
    Creates the tickers from the assets.

    :param assets: The asset to build the tickers from.

    :return: The list of tickers.
    """

    tickers = []

    for base in assets:
        for quote in assets:
            ticker = parts_to_ticker(base, quote)

            if base != quote and reverse_ticker(ticker) not in tickers:
                tickers.append(ticker)
            # end if
        # end for
    # end for

    return tickers
# end assets_to_tickers