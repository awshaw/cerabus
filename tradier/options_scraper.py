import logging
import os
import random
import re
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

import utils


class Tradier(object):
    def __init__(self, start, end, auth_token, base="https://sandbox.tradier.com/v1"):
        """ Class to instantiate and utilize the Tradier API

        Args:
            start (str): Desired start date for scraping date, of form YYYY-MM-DD
            end (str): Desired end date of form YYYY-MM-DD
            auth_token (str): Tradier API TOKEN
            url (str, optional): API url. Defaults to "https://sandbox.tradier.com/v1".
        """
        self.base = base
        self.headers = {"Accept": "application/json",
                        "Authorization": "Bearer {}".format(auth_token)}

        self.start = start
        self.end = end

        logging.basicConfig(format="%(levelname)s: %(created)f | %(message)s",
                            filename="scraper.log", level=logging.WARNING)
        self.logger = logging.getLogger(__name__)

    def request(self, path, params={}):
        """ Wrapper function to make a request.

        Args:
            path (str): Request path
            params (dict, optional): HTTP requests parameters. Defaults to {}.

        Returns:
            dict: Resulting JSON dict 
        """
        status_code = 0
        while (status_code != 200):
            r = requests.get(f"{self.base}/{path}",
                             params=params, headers=self.headers)

            status_code = r.status_code
            self.logger.info(f"Status code for {r.url}: {status_code}")
            if (status_code != 200):
                self.logger.warn(
                    "Status code not OK. Sleeping for 60 seconds.")
                time.sleep(60)
        try:
            result = r.json()
        except:
            return r

        return result

    def get_options(self, ticker):
        """ Get option tickers for a specific ticker

        Args:
            ticker (str): Ticker of interest

        Returns:
            pd.DataFrame: DataFrame with columns=["symbols", "options"]
        """
        result = pd.DataFrame(columns=["symbols", "options"])
        for t in ticker:
            self.logger.info(
                f"Scraping options symbols for {t} from {self.start} to {self.end}")
            _tmp = self.request("markets/options/lookup", {"underlying": t})
            _tmp = pd.DataFrame([{"symbols": y["rootSymbol"], "options": y["options"], "strikes": list(
                map(utils.get_option_strike, y["options"]))} for y in [x for x in _tmp["symbols"]]])

            result = pd.concat([result, _tmp])
        return result.reset_index().drop(["index"], axis=1)

    def get_history(self, ticker, interval="daily"):
        """ Get the quote history for a ticker over some interval.

        Args:
            ticker (str): Ticker of interest.
            interval (str, optional): Defaults to "daily". Options are daily, weekly, monthly.

        Returns:
            pd.DataFrame: DataFrame containing historical quotes.
        """
        result = self.request("markets/history", {"symbol": ticker,
                                                  "start": self.start,
                                                  "end": self.end,
                                                  "interval": "daily"})
        if (result['history'] is None):
            result = pd.DataFrame()
        elif result['history'] is not None:
            try:
                result = pd.DataFrame(result['history']['day'])
                result = result.set_index(pd.DatetimeIndex(result['date']))
            except:
                result = pd.DataFrame()

        return result

    def get_options_expirations(self, ticker, include_all_roots="true", strikes="true", **kwargs):
        """ Get the most recent expiration dates for a ticker's option chain.

        Args:
            ticker (str):  Ticker of interest.
            include_all_roots (str, optional): Defaults to "true". Other option is "false".
            strikes (str, optional): Defaults to "true". Other option is "false".

            Keyword Args:
                strike (int): The strike price.
                range (int): The range of strike prices to be requested. 


        Returns:
            pd.DataFrame: A dataframe containing the expirations dates (and the strikes, if possible)
        """
        result = self.request("markets/options/expirations", {"symbol": ticker,
                                                              "includeAllRoots": include_all_roots, "strikes": strikes})

        if strikes == "false":
            result = pd.DataFrame([{"date": y}
                                   for y in result["expirations"]["date"]])
        else:
            result = pd.json_normalize(result["expirations"]["expiration"])
            result.columns = ["date", "strikes"]

            if kwargs.get("strike") is None:
                _history = self.get_history(ticker)
                strike = int(_history.iloc[_history.index.get_loc(
                    pd.to_datetime(self.start), method='nearest')]['close'])
                range = 3
                del(_history)

            def range_filter(row):
                _r = np.array(row)
                return _r[np.where(np.logical_and(_r >= int(strike - range), _r <= int(strike + range)))]

            result["strikes"] = result["strikes"].apply(range_filter)

        return result

    def get_options_chain(self, ticker, params={}, greeks="true", opt_types=["C", "P"], **kwargs):
        """ Get options chain for a specific ticker. This may include pre-calculated 
        Greeks. This method will use the expiration dates from get_options_expirations() in order
        to request the options chain (in which case, the kwargs should be specified for a larger option chain). But,
        this option should ideally be avoided, since it will require more requests in comparison to requesting the entire
        option chain for any given ticker.

        If the HTTP request parameters are specified, get_options_expirations() will not be used. 
        This will result in the entire option chain for a ticker of a specific expiration date to be requested. 
        The expiration date must be specified within the dict (the key is "expiration").

        Args:
            ticker (str): [description]
            greeks (str, optional): Defaults to "true". Other value is "false".
            opt_types (list, optional): Defaults to Calls and Puts.

            Keyword Args:
                strike (int): The strike price.
                range (int): The range of strike prices to be requested. 
        """
        # if params is None:
        #     assert kwargs.get("strike") is not None & kwargs.get(
        #         "range") is not None
        #     strike = kwargs.get("strike")
        #     range = kwargs.get("range")

        #     expirations = self.get_options_expirations(ticker, strike, range)
        #     tickers = []
        #     for t in opt_types:
        #          tickers.append([utils.build_option_ticker(
        #             ticker, x, t, z) for z in y for x, y in expirations.values])
        #     tickers = np.array(tickers).flatten()
        #     result = self.request("markets/quotes", {"symbols": ",".join(tickers), "greeks": greeks})
        #     result = pd.json_normalize(result["quotes"]["quote"])
        # else:
        if params is not None: 
            result = self.request("markets/options/chains", params)
            result = pd.json_normalize(result["options"]["option"])
        return result
