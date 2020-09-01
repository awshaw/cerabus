import re
from datetime import datetime


def build_option_ticker(ticker, expiration_date, option_type, strike):
    """ Helper to build an option ticker

    Args:
        ticker (str): Ticker of interest.
        expiration_date (str): The expiration date (with format "%Y-%m-%d").
        option_type (str): The option type ("C" or "P").
        strike (str | int): The strike price.

    Returns:
        str: An option ticker of the form: {$SYMBOL}{YYMMDD}{P|C}{:05}000.
    """
    expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").strftime("%y%m%d") 
    return "{:s}{:s}{:s}{:05}000".format(ticker, expiration_date, option_type, int(strike))

def get_option_strike(ticker):
    """ Parse the strike price of a given ticker

    Args:
        ticker (str): An option ticker of the form: {$SYMBOL}{YYMMDD}{P|C}{:05}000.

    Returns:
        int: The parsed strike price.
    """
    regex = r"(?<=C|P)\d+"
    m = re.search(regex, ticker)

    assert len(m.groups()) == 0
    return int(m.group()[:-3])

def get_option_type(ticker):
    """ Parses the option type (Call or Put)

    Args:
        ticker (str): An option ticker of the form: {$SYMBOL}{YYMMDD}{P|C}{:05}000

    Returns:
        str: The option type (where C is a call, and P is a put option)
    """
    regex = r"C|P(?=\d+)"
    m = re.search(regex, ticker)

    assert len(m.groups()) == 0
    return m.group()

def strikes_filepath(*args):
    """ Helper method to generate filepath for option strike/symbol information.

    Returns:
        list(str): List of tickers
    """
    assert len(*args) > 0
    return datetime.now().strftime("%y_%m_%d_%Hh%mm") + "_" + "_".join(map(str, *args)) + "_strikes.csv"


def utc_to_datetime(timestamp):
    """ Helper to transform a UTC timestamp to a formatted datetime (YYYY-MM-DD HH:mm:ss)

    Args:
        timestamp (str): A UTC timestamp

    Returns:
        str: The formatted timestamp
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

