import datetime
import pandas as pd
import shioaji as sj
from shioaji import contracts
import os
from time import sleep
import json
from mypylib import get_trade_days
from typing import Union
from collections import defaultdict
from mypylib import parse_date_time


# {"AskPrice": [46.9, 46.95, 47.0, 47.2, 47.3],
#  "AskVolume": [3, 1, 5, 9, 12],
#  "BidPrice": [46.75, 46.6, 46.5, 46.45, 46.4],
#  "BidVolume": [1, 24, 16, 11, 33],
#  "Date": "2022/06/07",
#  "Time": "09:01:41.876574"
#  }
class Quote(dict):
    def __init__(self, *args):
        super().__init__(*args)
        self.Ask: Union[dict, None] = None
        self.Bid: Union[dict, None] = None
        self.timestamp = None

    def ts(self) -> datetime :
        if self.timestamp is None:
            # self.timestamp = datetime.datetime.strptime(f'{self.Date()} {self.Time()}', '%Y/%m/%d %H:%M:%S.%f')
            self.timestamp = parse_date_time(self.Date(), self.Time())
        return self.timestamp

    def Simtrade(self) -> int:
        value = super().get('Simtrade')
        return value[0] if isinstance(value, list) else value

    def AskPrice(self) -> list[float]:
        return super().get('AskPrice')

    def AskVolume(self) -> list[int]:
        return super().get('AskVolume')

    def BidPrice(self) -> list[float]:
        return super().get('BidPrice')

    def BidVolume(self) -> list[int]:
        return super().get('BidVolume')

    def Date(self) -> str:
        return super().get('Date')

    def Time(self) -> str:
        return super().get('Time')

    def Pause(self) -> int:
        return super().get('Pause')

    def TradeType(self) -> int:
        return super().get('TradeType')

    def BestBuy(self) -> int:
        return super().get('BestBuy')

    def BestSell(self) -> int:
        return super().get('BestSell')

    # 'AskPrice': [14.4, 14.45, 14.5, 14.55, 14.6], 'AskVolume': [2239, 370, 428, 88, 316]
    # {14.4: 2239, 14.45: 370, 14.5: 428, 14.55: 88, 14.6: 316}
    def zipAsk(self):
        if self.Ask is None:
            self.Ask = defaultdict(int, dict(zip(self.AskPrice(), self.AskVolume())))

    def zipBid(self):
        if self.Bid is None:
            self.Bid = defaultdict(int, dict(zip(self.BidPrice(), self.BidVolume())))


# {"AmountSum": [65246500.0],
#  "Close": [415.5],
#  "Date": "2022/06/07",
#  "TickType": [2],
#  "Time": "09:01:41.845465",
#  "VolSum": [156],
#  "Volume": [3]}
class Market(dict):
    def __init__(self, *args):
        super().__init__(*args)
        self.Ask: Union[dict, None] = None
        self.Bid: Union[dict, None] = None
        self.timestamp = None

    def ts(self) -> datetime:
        if self.timestamp is None:
            # self.timestamp = datetime.datetime.strptime(f'{self.Date()} {self.Time()}', '%Y/%m/%d %H:%M:%S.%f')
            self.timestamp = parse_date_time(self.Date(), self.Time())
        return self.timestamp

    def Simtrade(self) -> int:
        value = super().get('Simtrade')
        return value[0] if isinstance(value, list) else value

    def AmountSum(self) -> int:
        value = super().get('AmountSum')
        return value[0] if isinstance(value, list) else value

    def Close(self) -> float:
        value = super().get('Close')
        return value[0] if isinstance(value, list) else value

    def Date(self) -> str:
        return super().get('Date')

    def TickType(self) -> int:
        value = super().get('TickType')
        return value[0] if isinstance(value, list) else value

    def Time(self) -> str:
        return super().get('Time')

    def VolSum(self) -> int:
        value = super().get('VolSum')
        return value[0] if isinstance(value, list) else value

    def Volume(self) -> int:
        value = super().get('Volume')
        return value[0] if isinstance(value, list) else value

    def Pause(self) -> int:
        return super().get('Pause')

    def TradeType(self) -> int:
        return super().get('TradeType')

    def BestBuy(self) -> int:
        return super().get('BestBuy')

    def BestSell(self) -> int:
        return super().get('BestSell')

    def AskPrice(self) -> list[float]:
        return super().get('AskPrice', None)

    def AskVolume(self) -> list[int]:
        return super().get('AskVolume', None)

    def BidPrice(self) -> list[float]:
        return super().get('BidPrice', None)

    def BidVolume(self) -> list[int]:
        return super().get('BidVolume', None)

    def zipAsk(self):
        if self.Ask is None:
            self.Ask = defaultdict(int, dict(zip(self.AskPrice(), self.AskVolume())))

    def zipBid(self):
        if self.Bid is None:
            self.Bid = defaultdict(int, dict(zip(self.BidPrice(), self.BidVolume())))


class SJ_wrapper:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

        print(f'使用正式帳號')
        self.api = sj.Shioaji()
        self.api.login(self.api_key, self.secret_key, contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."))


class SJ_downloader(SJ_wrapper):
    def __init__(self, api_key, secret_key):
        super(SJ_downloader, self).__init__(api_key, secret_key)

        self.ticks = None

    def download_ticks(self, contract: contracts, date: Union[str, datetime.datetime]):
        print(contract, date)
        ticks = self.api.ticks(contract=contract, date=date if isinstance(date, str) else datetime.datetime.strftime('%Y-%m-%d'))
        self.ticks = ticks
        return ticks

    def save_ticks(self, filename):
        df = pd.DataFrame({**self.ticks})
        df.ts = pd.to_datetime(df.ts)

        df.to_csv(filename)


def unit_test_SJ_downloader():
    downloader = SJ_downloader(api_key='6Dkp67EVdMQBWE8Z6DZ5zPQAFTbvVPxEGzAEFiZ5ByhN',
                               secret_key='2NCQAhfP73PfKYaAi8xJVHZSp4Y91mSNViiFU7zQ19T2')

    if not os.path.isfile('trade_days.txt'):
        trade_days = get_trade_days('2018-01-01', datetime.datetime.today())
        trade_days.reverse()
        with open('trade_days.txt', 'w+') as fp:
            json.dump(trade_days, fp)
    else:
        with open('trade_days.txt') as fp:
            trade_days = json.load(fp)

    for day in trade_days:
        print(day)
        file = f'days/TXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.TXF.TXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/EXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.EXF.EXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)

        file = f'days/FXF-{day}.txt'
        if not os.path.isfile(file):
            downloader.download_ticks(contract=downloader.api.Contracts.Futures.FXF.FXFR1, date=day)
            downloader.save_ticks(file)

            sleep(3)


def converter_SJ_ticks_to_MC():
    files = os.listdir('days')
    files.sort()
    print(files)

    with open('EXF_ticks_for_MC.txt', 'w+') as ex:
        with open('FXF_ticks_for_MC.txt', 'w+') as fx:
            with open('TXF_ticks_for_MC.txt', 'w+') as tx:
                fp = None
                for file in files:
                    if file[0:3] == 'EXF':
                        fp = ex
                    if file[0:3] == 'FXF':
                        fp = fx
                    if file[0:3] == 'TXF':
                        fp = tx


if __name__ == '__main__':

    if True:
        unit_test_SJ_downloader()

    if False:
        converter_SJ_ticks_to_MC()
