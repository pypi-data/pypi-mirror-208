import os
from datetime import date
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from longalpha_data.utils.constants import (
    US_STOCK_MARKET_HOLIDAYS_BUCKET,
    US_STOCK_MARKET_HOLIDAYS_FILE,
)
from longalpha_data.utils.utils import get
from minio.error import S3Error

from longalpha_utils.utils import MinioParquet


class USStockHolidays:
    def __init__(
            self, polygon_key: str, minio_endpoint: str, access_key: str, secret_key: str
    ):
        self.polygon_key = polygon_key
        self.minio_endpoint = minio_endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def download_upcoming_us_stock_holidays(self) -> pd.DataFrame:
        """
        downloaders upcoming US stock market holidays using polygon api

        Args:
            api_key: polygon api key

        Returns: a dataframe as follows:
                     date exchange       name  status
        0  2022-12-26     NYSE  Christmas  closed
        1  2022-12-26   NASDAQ  Christmas  closed

        """
        endpoint = (
            f"https://api.polygon.io/v1/marketstatus/upcoming?apiKey={self.polygon_key}"
        )
        holidays = get(endpoint)
        return pd.DataFrame(holidays)

    def get_all_us_stock_holidays(self) -> pd.DataFrame:
        """
        downloaders upcoming US stock market holidays using polygon api and combine upcoming holidays with
        existing holiday. The function has a side effect which saves stock holiday as a parquet file.

        Args:
            api_key: polygon api key

        Returns: a dataframe as follows:
                     date exchange       name  status
        0  2022-12-26     NYSE  Christmas  closed
        1  2022-12-26   NASDAQ  Christmas  closed

        """
        mw = MinioParquet(self.minio_endpoint, self.access_key, self.secret_key)
        try:
            current_holidays = mw.get(
                US_STOCK_MARKET_HOLIDAYS_BUCKET, US_STOCK_MARKET_HOLIDAYS_FILE
            )
        except S3Error as e:
            if "The specified key does not exist" in e.message:
                current_holidays = pd.DataFrame()
            else:
                raise Exception("unknown Exception")
        upcoming_holidays = self.download_upcoming_us_stock_holidays()
        holidays = pd.concat([current_holidays, upcoming_holidays]).drop_duplicates(
            ignore_index=True
        )
        mw.put(holidays, US_STOCK_MARKET_HOLIDAYS_BUCKET, US_STOCK_MARKET_HOLIDAYS_FILE)
        return holidays

    def is_us_stock_market_closed_today(self, date: date = None) -> bool:
        """
        checkers if today is a US stock market is closed for today.Note that the status is based on date, not time.
        Thus, if the stock market is closed at 9:00PM EST, the function should output false. A stock market is closed
        if and only if it's a holiday or it's not a business day. Note that early close trading days are not counted as
        closed.

        Args:
            my_api_key: polygon api key
            date: date in the format of 2022-01-01. If it is None, the function will use today's date as date.

        Returns: True or False

        """
        if date is None:
            date = datetime.today()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        if date.weekday() in [5, 6]:
            return True
        holidays = self.get_all_us_stock_holidays()
        closed_holidays = holidays.loc[holidays["status"] == "closed"]
        if str(date) in closed_holidays["date"].to_list():
            return True
        return False


if __name__ == "__main__":
    load_dotenv()
    ush = USStockHolidays(
        polygon_key=os.environ["POLYGON"],
        minio_endpoint=os.environ["MINIO_API"],
        access_key=os.environ["MINIO_ACCESS_KEY"],
        secret_key=os.environ["MINIO_SECRET_KEY"],
    )
    ush.download_upcoming_us_stock_holidays()
    ush.get_all_us_stock_holidays()
    x = ush.is_us_stock_market_closed_today()
    print(x)
