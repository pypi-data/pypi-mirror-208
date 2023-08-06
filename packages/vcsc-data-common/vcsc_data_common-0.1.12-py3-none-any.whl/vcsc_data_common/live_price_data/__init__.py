import json
import logging
from deltalake import DeltaTable
import pandas as pd
import requests
from enum import Enum


class MarketStatus(Enum):
    STARTED = 'STARTED',  # sẵn sàng nhận lệnh
    ATO = 'ATO',
    LO_MORNING = 'LO_MORNING',
    LO_AFTERNOON = 'LO_AFTERNOON',
    ATC = 'ATC',
    ENDED = 'ENDED',  # ngưng nhận lệnh
    CLOSED = 'CLOSED',  # đóng cửa
    LUNCH_BREAK = 'LUNCH_BREAK',
    EXTEND_HOUR = 'EXTEND_HOUR'  # phiên 2h45 -> 3h HNX, UPCOM


class DataFetcher:
    last_modification_time: str

    def __init__(self, aws_access_key: str, aws_secret_key: str, time_frame: str, is_fill_gap: bool) -> None:
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.time_frame = time_frame
        self.is_fill_gap = is_fill_gap

        self.uri = f"s3://vcsc-ai/prod/price_data/{self.time_frame}_none_gap_intraday" if is_fill_gap else f"s3://vcsc-ai/prod/price_data/{self.time_frame}_intraday"

    def get_data(self) -> pd.DataFrame:
        dt = DeltaTable(self.uri, storage_options={
            "AWS_ACCESS_KEY_ID": self.aws_access_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_key,
            'AWS_REGION': "ap-southeast-1"
        })

        pyarrow_table = dt.to_pyarrow_table()

        df: pd.DataFrame = pyarrow_table.to_pandas()

        return df

    def get_latest_modification_time(self):
        dt = DeltaTable(self.uri, storage_options={
            "AWS_ACCESS_KEY_ID": self.aws_access_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_key,
            'AWS_REGION': "ap-southeast-1"
        })

        actions_df = dt.get_add_actions().to_pandas()
        self.last_modification_time = actions_df.iloc[0]['modification_time']
        return self.last_modification_time

    def get_market_status(self) -> pd.DataFrame:

        response = requests.get(
            'https://mt.vietcap.com.vn/api/price/marketStatus/getAll')
        try:

            json_data = json.loads(response.text)
            arr = []
            for key in json_data:
                arr.append(
                    {'marketCode': json_data[key]['marketCode'], 'status': json_data[key]['status']})

        except Exception as e:
            logging.error(f'response {response.text}')
            raise e

        return pd.DataFrame(arr)
