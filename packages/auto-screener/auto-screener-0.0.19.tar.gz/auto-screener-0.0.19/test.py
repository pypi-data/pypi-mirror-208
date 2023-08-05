# test.py

from auto_screener.progress import Spinner
from auto_screener.screening import MultiScreener
from auto_screener.collect import collect_mutual_tickers

MATCHES = [["USD", "USDT"]]
QUOTES = ["USD", "USDT"]
EXCHANGES = ["kraken", "kucoin"]

LENGTH = 0
DELAY = 1

PRO = True

INTERVAL = "1m"
LOCATION = "datasets"

def main() -> None:
    """Runs the program to test the module."""

    exchanges = collect_mutual_tickers(
        exchanges=EXCHANGES, quotes=QUOTES
    )

    screener = MultiScreener(
        exchanges=exchanges, length=LENGTH,
        delay=DELAY, location=LOCATION,
        pro=PRO, interval=INTERVAL
    )

    with Spinner(message='Initializing Screeners'):
        screener.initialize_screeners()
    # end Spinner

    screener.run(block=True)
# end main

if __name__ == "__main__":
    main()
# end if