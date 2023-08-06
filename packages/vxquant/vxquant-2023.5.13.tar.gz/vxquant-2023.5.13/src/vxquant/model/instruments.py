"""股票池"""
import datetime
import polars as pl
from pathlib import Path
from typing import List, Union, Dict
from vxquant.model.nomalize import to_symbol
from vxutils import to_datetime, vxtime, to_timestamp, logger
from vxquant.model.typehint import DateTimeType, InstrumentType


def is_in_periods(dt, periods):
    dt = to_timestamp(dt) * 1_000_000
    return any(period[0] <= dt <= period[1] for period in periods)


class vxInstruments:
    """股票池类"""

    def __init__(self, name: str, registrations: pl.DataFrame = None):
        self._name = name
        self._registrations = (
            registrations.with_columns(
                [
                    pl.col("start_date").apply(to_datetime),
                    pl.col("end_date").apply(to_datetime),
                ]
            )
            if registrations is not None
            else pl.DataFrame(
                {"symbol": [], "start_date": [], "end_date": [], "weight": []},
                schema={
                    "symbol": pl.Utf8,
                    "start_date": pl.Datetime,
                    "end_date": pl.Datetime,
                    "weight": pl.Float64,
                },
            )
        )
        self._last_updated_dt = (
            to_datetime(vxtime.today())
            if self._registrations.height == 0
            else self._registrations["end_date"].max()
        )

    @property
    def name(self) -> str:
        """股票池名称"""
        return self._name

    def __str__(self) -> str:
        return (
            f"< 证券池({self._name}) 最近更新日期"
            f":{self._last_updated_dt:%Y-%m-%d}"
            f" 最新证券:\n {self.list_instruments(self._last_updated_dt)} >"
        )

    @property
    def registrations(self) -> pl.DataFrame:
        """股票池出入注册表

        Returns:
            pl.DataFrame -- 注册表
        """
        return self._registrations

    @property
    def last_updated_dt(self) -> DateTimeType:
        """最近更新日期

        Returns:
            DateTimeType -- 日期类型:datetime类型
        """
        return self._last_updated_dt

    def list_instruments(self, trade_date: DateTimeType = None) -> List[InstrumentType]:
        """列出股票池中的证券

        Keyword Arguments:
            trade_date {DateTimeType} -- 交易日，若为空，则为当前日期 (default: {None})

        Returns:
            List[InstrumentType] -- 股票列表
        """
        trade_date = min(
            to_datetime(trade_date or vxtime.today()), self._last_updated_dt
        )

        inst = self._registrations.filter(
            ((pl.col("start_date") <= trade_date) & (pl.col("end_date") >= trade_date))
        )

        return inst["symbol"].to_list()

    def get_weights(self, trade_date: DateTimeType = None) -> Dict[str, float]:
        """获取权重信息

        Keyword Arguments:
            trade_date {DateTimeType} -- 交易日，若为空，则为当前日期 (default: {None})

        Returns:
            Dict[str,float] -- 权重信息
        """
        trade_date = min(
            to_datetime(trade_date or vxtime.today()), self._last_updated_dt
        )

        inst = self._registrations.filter(
            ((pl.col("start_date") <= trade_date) & (pl.col("end_date") >= trade_date))
        )
        return dict(*inst.select(["symbol", "weight"]).to_struct().arr)

    def add_instrument(
        self,
        symbol: InstrumentType,
        start_date: DateTimeType,
        end_date: DateTimeType = None,
        weight: float = 1.0,
    ):
        try:
            symbol = to_symbol(symbol)
            start_date = to_datetime(start_date)
            end_date = to_datetime(end_date) if end_date else start_date
        except Exception as e:
            logger.error(f"ValueError: {e}")
            return

        self._registrations.vstack(
            pl.DataFrame(
                [
                    {
                        "symbol": symbol,
                        "start_date": start_date,
                        "end_date": end_date,
                        "weight": weight,
                    }
                ]
            ),
            in_place=True,
        )
        return self

    def update_components(
        self,
        instruments: Union[List[InstrumentType], Dict[InstrumentType, float]],
        updated_dt: DateTimeType = None,
    ):
        """按增量更新股票池"""

        updated_dt = to_datetime(updated_dt or vxtime.today())
        if (not self._registrations.is_empty()) and self._last_updated_dt >= updated_dt:
            raise ValueError(
                f"updated_dt( {updated_dt:%Y-%m-%d} ) 小于当前更新时间:"
                f" {self._last_updated_dt:%Y-%m-%d}"
            )

        if isinstance(instruments, (list, tuple)):
            instruments = {inst: 1 for inst in instruments}

        new_instruments = pl.DataFrame(
            [
                {"symbol": symbol, "end_date": self._last_updated_dt, "weight": weight}
                for symbol, weight in instruments.items()
            ]
        )

        self._registrations = (
            self._registrations.join(
                new_instruments, on=["symbol", "end_date"], how="outer"
            )
            .with_columns(
                [
                    pl.col("start_date").fill_null(updated_dt),
                    pl.when(
                        (pl.col("end_date") == self._last_updated_dt)
                        & (pl.col("symbol").is_in(new_instruments["symbol"]))
                    )
                    .then(pl.lit(updated_dt))
                    .otherwise(pl.col("end_date"))
                    .alias("end_date"),
                    pl.when(
                        (pl.col("end_date") == self._last_updated_dt)
                        & (pl.col("symbol").is_in(new_instruments["symbol"]))
                    )
                    .then(pl.col("weight_right"))
                    .otherwise(pl.col("weight"))
                    .alias("weight"),
                ]
            )
            .select(["symbol", "start_date", "end_date", "weight"])
            .sort(by="end_date")
        )
        self._last_updated_dt = updated_dt
        return self

    @classmethod
    def load(cls, name, instruments_parquet: Union[str, Path]) -> "vxInstruments":
        registrations = pl.read_parquet(instruments_parquet)
        return vxInstruments(name, registrations)

    def dump(self, instruments_parquet: Union[str, Path]) -> None:
        """保存相关信息"""
        if Path(instruments_parquet).is_dir():
            instruments_parquet = Path(instruments_parquet, f"{self._name}.parquet")

        self._registrations.write_parquet(instruments_parquet)
        logger.info(f"股票池:{self._name} 保存{instruments_parquet.as_posix()} 完成。")
        return self

    def rebuild(self) -> "vxInstruments":
        """重建登记表"""

        new_registrations = []
        temp_registrations = {}

        for rows in self._registrations.sort(by=["symbol", "start_date"]).iter_rows(
            named=True
        ):
            symbol = rows["symbol"]

            if symbol not in temp_registrations:
                temp_registrations[symbol] = rows
            elif (
                temp_registrations[symbol]["end_date"] + datetime.timedelta(days=1)
                >= rows["start_date"]
                and temp_registrations[symbol]["end_date"] < rows["end_date"]
            ):
                temp_registrations[symbol]["end_date"] = rows["end_date"]

            elif (temp_registrations[symbol]["end_date"]) < rows["start_date"]:
                new_registrations.append(temp_registrations[symbol])
                temp_registrations[symbol] = rows

        new_registrations.extend(temp_registrations.values())
        self._registrations = pl.DataFrame(new_registrations)
        return self

    def all_instruments(self) -> List[InstrumentType]:
        return self._registrations["symbol"].to_list()

    def union(self, other: "vxInstruments") -> "vxInstruments":
        """合并另外一个股票池"""
        self._registrations = pl.concat([self._registrations, other._registrations])
        self.rebuild()
        return self

    def intersect(self, other: "vxInstruments") -> "vxInstruments":
        """交集"""

        new_registrations = []
        for rows in self.registrations.sort(["symbol", "start_date"]).iter_rows(
            named=True
        ):
            new_registrations.extend(
                {
                    "symbol": rows["symbol"],
                    "start_date": max(rows["start_date"], other_rows["start_date"]),
                    "end_date": min(rows["end_date"], other_rows["end_date"]),
                    "weight": rows["weight"],
                }
                for other_rows in other.registrations.filter(
                    (pl.col("start_date") < rows["end_date"])
                    & (pl.col("end_date") > rows["start_date"])
                    & (pl.col("symbol") == rows["symbol"])
                ).iter_rows(named=True)
            )

        self._registrations = (
            pl.DataFrame(new_registrations)
            if new_registrations
            else pl.DataFrame(
                {"symbol": [], "start_date": [], "end_date": [], "weight": []},
                schema={
                    "symbol": pl.Utf8,
                    "start_date": pl.Datetime,
                    "end_date": pl.Datetime,
                    "weight": pl.Float64,
                },
            )
        )

        self.rebuild()
        return self

    def difference(self, other: "vxInstruments") -> "vxInstruments":
        """差集"""
        new_registrations = []
        for rows in self.registrations.sort(["symbol", "start_date"]).iter_rows(
            named=True
        ):
            for other_rows in (
                other.registrations.filter(
                    (pl.col("start_date") <= rows["end_date"])
                    & (pl.col("end_date") >= rows["start_date"])
                    & (pl.col("symbol") == rows["symbol"])
                )
                .sort("start_date")
                .iter_rows(named=True)
            ):
                if rows["start_date"] < other_rows["start_date"]:
                    new_registrations.append(
                        {
                            "symbol": rows["symbol"],
                            "start_date": rows["start_date"],
                            "end_date": other_rows["start_date"] - datetime.timedelta(
                                days=1
                            ),
                            "weight": rows["weight"],
                        }
                    )

                rows["start_date"] = other_rows["end_date"] + datetime.timedelta(days=1)

                if rows["start_date"] > rows["end_date"]:
                    break

            if rows["start_date"] <= rows["end_date"]:
                new_registrations.append(rows)

        self._registrations = pl.DataFrame(new_registrations)
        self.rebuild()
        return self


if __name__ == "__main__":
    a = vxInstruments("test")
    a.add_instrument("SHSE.600000", "2022-01-01", "2022-02-28")
    a.add_instrument("SHSE.600000", "2022-03-6", "2022-04-30")
    # a.add_instrument("SHSE.600000", "2022-02-01", "2022-03-05")
    # a.add_instrument("SHSE.600001", "2022-01-01", "2022-02-28")
    # a.add_instrument("SHSE.600001", "2022-03-12", "2022-04-30")
    # print(a.registrations)
    b = vxInstruments("b")

    b.add_instrument("SHSE.600000", "2022-02-14", "2022-03-12")
    b.add_instrument("SHSE.600000", "2021-01-01", "2022-01-12")

    print("-" * 60)
    print(b.registrations)
    print("-" * 60)

    # print(b.registrations)
    # with vxtime.timeit(1):
    #    a.union(b)
    # print(a.registrations)
    with vxtime.timeit():
        a.difference(b)
        # a.union(b)
    print(a.registrations)
