import asyncio
import configparser

from iex import IEX
from options import Options

config = configparser.ConfigParser()
config.read("config.cfg")

def main():
    o = Options(config["IEX"]["base"], config["IEX"]["token"])

    symbols = ["AAPL", "SPY"]
    asyncio.run(o.get_expirations(symbols))

if __name__ == '__main__':
    main()
