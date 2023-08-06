from dataclasses import dataclass
from vcsc_data_common.live_price_data import DataFetcher as LiveDataFetcher, MarketStatus
from vcsc_data_common.offline_price_data import DataFetcher as OfflineDataFetcher
import pandas as pd
import time
import logging
import threading


@dataclass
class FetchingTimeFrameConfig:
    time_frame: str
    is_fill_gap: bool = False


class IntervalFetching:
    offline_data_dfs: list[pd.DataFrame] = []
    live_data_dfs: list[pd.DataFrame] = []
    is_new_live_data: bool

    def __init__(self, aws_access_key: str, aws_secret_key: str, fetching_time_frame_configs: list[FetchingTimeFrameConfig], interval: int, callback: callable) -> None:
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.fetching_time_frame_configs = fetching_time_frame_configs
        self.callback = callback
        self.interval = interval
        self.live_modification_time = None
        self.live_data_fetchers: list[LiveDataFetcher] = []
        self.offline_data_fetchers: list[OfflineDataFetcher] = []

        for fetching_time_frame_config in fetching_time_frame_configs:

            live_data_fetcher = LiveDataFetcher(
                aws_access_key, aws_secret_key, fetching_time_frame_config.time_frame, fetching_time_frame_config.is_fill_gap)
            offline_data_fetcher = OfflineDataFetcher(
                aws_access_key, aws_secret_key, fetching_time_frame_config.time_frame, fetching_time_frame_config.is_fill_gap)

            self.live_data_fetchers.append(live_data_fetcher)
            self.offline_data_fetchers.append(offline_data_fetcher)

            self.offline_data_dfs.append(pd.DataFrame())
            self.live_data_dfs.append(pd.DataFrame())

    def start(self):
        self.offline_data_df = self.fetch_all_offline_data()

        while True:

            self.fetch_all_live_data()

            if(self.is_new_live_data):

                # union all df & return
                data_arr: list[pd.DataFrame] = []

                for index in range(self.fetching_time_frame_configs.__len__()):
                    offline_data_df = self.offline_data_dfs[index]
                    live_data_df = self.live_data_dfs[index]
                    union_df = pd.concat([offline_data_df, live_data_df])

                    data_arr.append(union_df)

                market_status_df = self.live_data_fetchers[0].get_market_status(
                )

                self.callback(*data_arr, market_status_df,
                              self.live_modification_time)

            else:
                logging.debug('data has no change')

            self.is_new_live_data = False
            time.sleep(self.interval)

    def fetch_all_live_data(self):
        threads: list[threading.Thread] = []

        for idx, live_data_fetcher in enumerate(self.live_data_fetchers):
            threads.append(threading.Thread(
                target=self.fetch_live_data, args=(live_data_fetcher, idx)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def fetch_live_data(self, live_data_fetcher: LiveDataFetcher, result_index: int):
        new_live_modification_time = live_data_fetcher.get_latest_modification_time()

        if(self.live_modification_time != new_live_modification_time):

            live_data_df = live_data_fetcher.get_data()

            # bỏ những cây nến chưa complete trong LO_AFTERNOON và LO_MORNING
            live_data_df = self.filter_completed_candles(live_data_df)

            self.live_data_dfs[result_index] = live_data_df
            self.is_new_live_data = True
            self.live_modification_time = new_live_modification_time

    def fetch_all_offline_data(self):
        threads: list[threading.Thread] = []

        for idx, offline_data_fetcher in enumerate(self.offline_data_fetchers):
            threads.append(threading.Thread(
                target=self.fetch_offline_data, args=(offline_data_fetcher, idx)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def fetch_offline_data(self, offline_data_fetcher: OfflineDataFetcher, result_index: int):

        logging.debug(
            f'fetching offline data: {offline_data_fetcher.time_frame}')

        self.offline_data_dfs[result_index] = offline_data_fetcher.get_data()

    def filter_completed_candles(self, df: pd.DataFrame):

        market_status_df = self.live_data_fetchers[0].get_market_status()

        hnx_market_status = market_status_df[market_status_df['marketCode']
                                             == 'HNX'].iloc[-1]['status']

        if hnx_market_status in [MarketStatus.LO_AFTERNOON.name, MarketStatus.LO_MORNING.name]:
            max_trading_date = df['TradingDate'].max()

            return df[df['TradingDate'] < max_trading_date]

        return df
