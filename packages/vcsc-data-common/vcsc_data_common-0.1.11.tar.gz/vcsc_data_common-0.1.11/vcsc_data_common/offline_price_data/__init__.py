from deltalake import DeltaTable
import pandas as pd


class DataFetcher:

    def __init__(self, aws_access_key: str, aws_secret_key: str, time_frame: str, is_fill_gap: bool) -> None:
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.time_frame = time_frame
        self.is_fill_gap = is_fill_gap

        self.uri = f"s3://vcsc-ai/prod/price_data/{self.time_frame}_none_gap" if is_fill_gap else f"s3://vcsc-ai/prod/price_data/{self.time_frame}"

    def get_data(self) -> pd.DataFrame:

        dt = DeltaTable(self.uri, storage_options={
            "AWS_ACCESS_KEY_ID": self.aws_access_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_key,
            'AWS_REGION': "ap-southeast-1"
        })

        pyarrow_table = dt.to_pyarrow_table()

        df: pd.DataFrame = pyarrow_table.to_pandas()

        return df
