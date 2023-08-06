"""数据加载器"""

from pathlib import Path
from typing import Union, List
import polars as pl
from vxquant.model.contants import SecType
from vxquant.model.typehint import DateTimeType
from vxquant.model.instruments import vxInstruments
from vxutils import to_datetime, to_timestring, to_enum, logger, vxAPIWrappers


class vxDataLoader:
    """本地数据加载器"""

    def load_calendar(self) -> pl.Series:
        """加载交易日历"""

    def save_calendar(self, trade_dates: List[DateTimeType]) -> None:
        """添加交易日历"""

    def load_instruments(self, name: str = "cnstocks") -> vxInstruments:
        """加载股票池"""

    def save_instruments(self, instruments: vxInstruments) -> None:
        """添加股票池"""

    def load_features(
        self, period: str = "day", sec_type: SecType = SecType.STOCK
    ) -> pl.LazyFrame:
        """加载特征数据

        Keyword Arguments:
            period {str} -- 周期，可选: day 或 min (default: {"day"})
            sec_type {SecType} -- 证券类型 (default: {SecType.STOCK})

        Returns:
            pl.LazyFrame -- 返回特征数据LazyFrame格式
        """

    def save_features(
        self, data: pl.DataFrame, period: str = "day", sec_type: SecType = SecType.STOCK
    ) -> None:
        """保存特征数据

        Arguments:
            data {pl.DataFrame} -- 特征数据

        Keyword Arguments:
            period {str} -- 周期，可选: day 或 min (default: {"day"})
            sec_type {SecType} -- 证券类型 (default: {SecType.STOCK})
        """

    def load_factor(self, name: str) -> pl.LazyFrame:
        """加载因子数据

        Arguments:
            name {str} -- 因子名称

        Returns:
            pl.LazyFrame -- 返回因子数据LazyFrame格式
        """

    def save_factor(self, factor_datas: pl.DataFrame) -> None:
        """保存因子数据

        Arguments:
            factor_datas {pl.DataFrame} -- 因子数据
        """


class vxLocalDataLoader(vxDataLoader):
    """本地数据加载器"""

    def __init__(self, data_path: Union[str, Path] = None):
        if data_path is None:
            data_path = Path.home().joinpath(".data")
        if isinstance(data_path, str):
            data_path = Path(data_path)

        self._data_path = data_path
        self._data_path.joinpath("instruments").mkdir(parents=True, exist_ok=True)
        self._data_path.joinpath("features").mkdir(parents=True, exist_ok=True)
        self._data_path.joinpath("factors").mkdir(parents=True, exist_ok=True)
        logger.info(f"{self.__class__.__name__} init with data_path: {self._data_path}")

    def load_calendar(self) -> pl.Series:
        if self._data_path.joinpath("calendar.csv").exists():
            return (
                pl.read_csv(self._data_path.joinpath("calendar.csv"))
                .with_columns([pl.col("trade_date").apply(to_datetime)])
                .sort(by="trade_date")
            )
        return None

    def save_calendar(self, trade_dates: List[DateTimeType]) -> None:
        calendar_csv = self._data_path.joinpath("calendar.csv")
        calendar_df = pl.DataFrame({"trade_date": trade_dates})
        if calendar_csv.exists():
            save_trade_dates = pl.read_csv(calendar_csv)
            calendar_df = save_trade_dates.extend(calendar_df)
        calendar_df.select(
            pl.col("trade_date").apply(lambda x: to_timestring(x, "%Y-%m-%d")).unique()
        ).sort(by="trade_date").write_csv(calendar_csv)

    def load_instruments(self, name: str = "cnstocks") -> vxInstruments:
        instruments_csv = self._data_path.joinpath("instruments", f"{name}.csv")
        registrations = None
        if instruments_csv.exists():
            registrations = pl.read_csv(instruments_csv)
        return vxInstruments(name, registrations)

    def save_instruments(self, instruments: vxInstruments) -> None:
        instruments_csv = self._data_path.joinpath(
            "instruments", f"{instruments.name}.csv"
        )
        instruments.registrations.write_csv(instruments_csv)

    def load_industry_matrix(self, industry_classify):
        pass

    def save_industry_matrix(self, industry_matrix: pl.DataFrame) -> None:
        pass

    def load_features(
        self, period: str = "day", sec_type: SecType = SecType.STOCK
    ) -> pl.LazyFrame:
        period = period.lower()
        if period not in ["day", "min"]:
            raise ValueError(f"period must be day or min, but got {period}")
        sec_type = to_enum(sec_type, SecType)

        features_parquet = self._data_path.joinpath(
            "features", f"{period}_{sec_type.name.lower()}.parquet"
        )
        return pl.scan_parquet(features_parquet).with_columns(
            [
                pl.col("trade_date").str.strptime(pl.Datetime, "%Y-%m-%d"),
                pl.col("*")
                .exclude(["trade_date", "symbol"])
                .cast(pl.Float64, strict=False),
            ]
        )

    def save_features(
        self,
        data: pl.DataFrame,
        period: str = "day",
        sec_type: Union[str, SecType] = "STOCK",
    ) -> None:
        period = period.lower()

        if period not in ["day", "min"]:
            raise ValueError(f"period must be day or min, but got {period}")
        sec_type = to_enum(sec_type, SecType)

        features_parquet = self._data_path.joinpath(
            "features", f"{period}_{sec_type.name.lower()}.parquet"
        )
        data = data.with_columns(
            [
                pl.col("trade_date").dt.strftime("%Y-%m-%d"),
                pl.col("*")
                .exclude(["trade_date", "symbol"])
                .cast(pl.Float64, strict=False),
            ]
        ).sort(["trade_date", "symbol"])

        if features_parquet.exists():
            data = pl.read_parquet(features_parquet, use_pyarrow=True).extend(data)
        data.write_parquet(features_parquet)

    def load_factor(self, name: str) -> pl.LazyFrame:
        factor_parquet = self._data_path.joinpath("factors", f"{name}.parquet")
        return pl.scan_parquet(factor_parquet)

    def save_factor(self, factor_datas: pl.DataFrame) -> None:
        for name in factor_datas.columns:
            if name in ["trade_date", "symbol", "mask"]:
                continue

            factor_parquet = self._data_path.joinpath("factors", f"{name}.parquet")
            data = factor_datas.select(["trade_date", "symbol", name]).lazy()
            if factor_parquet.exists():
                data = pl.scan_parquet(factor_parquet).join(
                    data,
                    on=["trade_date", "symbol"],
                    how="outer",
                )
            data.sink_parquet(factor_parquet)


if __name__ == "__main__":
    loader = vxLocalDataLoader("/Volumes/work/quant/collector/data")
    print(loader.load_features("day", "STOCK").collect())
    # print(loader.save_calendar(["2020-01-01 3:30:20", "2021-01-02", "2021-01-03"]))
    # print(loader.load_calendar())
    # from vxutils import vxtime

    # vxtime.add_holidays(["2020-01-01 3:30:20", "2021-01-02", "2021-01-03"])
    # print(vxtime.is_holiday("2020-01-01"))
