"""本地文件接口"""
import polars as pl
from pathlib import Path
from typing import List, Union
from vxquant.providers.base import vxInstrumentsProvider, vxFeaturesProvider
from vxquant.model.instruments import vxInstruments
from vxquant.model.typehint import InstrumentType, DateTimeType
from vxquant.model.nomalize import normalize_freq, to_symbol
from vxutils import logger, to_datetime, vxtime


class vxLocalInstrumentsProvider(vxInstrumentsProvider):
    def __init__(self, data_dir: Union[str, Path] = None) -> None:
        self.instruments_dir = (
            Path(data_dir) if data_dir else Path.home().joinpath(".data")
        ).joinpath("instruments/")
        self.instruments_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"{self.__class__.__name__} 使用文件目录: {self.instruments_dir}")

    def __call__(self, instruments_name: str = "all") -> vxInstruments:
        registrations = pl.read_csv(
            self.instruments_dir.joinpath(f"{instruments_name}.csv")
        )
        if "weight" not in registrations.columns:
            registrations = registrations.select(
                [pl.col("*"), pl.lit(1).alias("weight")]
            )
        return vxInstruments(instruments_name, registrations)


class vxLocalFeaturesProvider(vxFeaturesProvider):
    def __init__(
        self,
        data_dir: Union[str, Path] = None,
        date_col: str = "trade_date",
        symbol_col: str = "symbol",
    ) -> None:
        self._features_dir = (
            Path(data_dir) if data_dir else Path.home().joinpath(".data")
        ).joinpath("features")
        self._features_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"{self.__class__.__name__} 使用文件目录: {self._features_dir}")
        self._date_col = date_col
        self._symbol_col = symbol_col

    def __call__(
        self,
        instruments: Union[List[InstrumentType], vxInstruments],
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
        freq: str = "1d",
        fields: List[str] = None,
    ) -> pl.DataFrame:
        start_date = to_datetime(start_date or "2005-01-01")
        end_date = to_datetime(end_date or vxtime.today())
        if isinstance(instruments, vxInstruments):
            instruments = instruments.all_instruments()
        freq, period = normalize_freq(freq)

        # freq = "day" if period == "1d" else "min"

        if fields is not None:
            fields = set(fields)
            fields.add(self._date_col)
            fields.add(self._symbol_col)
            fields = pl.col(*fields)
        else:
            fields = pl.col("*")

        data = pl.scan_parquet(Path(self._features_dir, f"features_{period}.parquet"))

        return (
            data.with_columns(
                [pl.col(self._date_col).str.strptime(pl.Datetime, "%Y-%m-%d")]
            )
            .filter(
                (pl.col(self._symbol_col).is_in(instruments))
                & (pl.col(self._date_col).is_between(start_date, end_date))
            )
            .drop_nulls()
            .sort([self._date_col, self._symbol_col])
            .collect()
            .select(fields)
        )
