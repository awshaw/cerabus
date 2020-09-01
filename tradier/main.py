import argparse
import os
from datetime import datetime

import numpy as np
import pandas as pd

import options_scraper
import utils

parser = argparse.ArgumentParser(
    description='Scrape price history for a specific ticker from Tradier.')
parser.add_argument('ticker', type=str, nargs='+',
                    help='a ticker to scrape price data for')
parser.add_argument('--start', type=str, nargs='?',
                    help='a start date')
parser.add_argument('--end', type=str, nargs='?',
                    help='a end date', default=datetime.today().strftime("%Y-%m-%d"))
parser.add_argument('--token', type=str, help='Tradier API key')

args = parser.parse_args()


def make_options_folder():
    """ Check if a folder exists for data """
    return os.mkdir("options") if os.path.isdir("options") != True else print("Folder exists!")

# TODO need to clean up function arguments. This aint it cheif
def options_downloader(ticker, start, end, token):
    api = options_scraper.Tradier(start, end, auth_token=token)
    return api.get_options_chain(ticker, params={"symbol": ticker, "expiration": "2020-09-18"})

if __name__ == "__main__":
    make_options_folder()
    for t in args.ticker:
        x = options_downloader(t, args.start, args.end, args.token)
        x.to_csv(utils.strikes_filepath(t))
