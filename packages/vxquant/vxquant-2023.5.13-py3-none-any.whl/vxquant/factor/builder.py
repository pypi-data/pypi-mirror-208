"""因子构建类"""
import re
import polars as pl
from tqdm import tqdm
from typing import Dict, List, Union
from vxquant.model.typehint import DateTimeType
from vxquant.model.instruments import vxInstruments
from vxquant.apis import vxMdAPI
from vxquant.factor.expr.ops import *
from vxquant.factor.loader import vxLocalDataLoader
from vxutils import vxtime, to_datetime, logger, vxWrapper


def to_expr(name: str, feature: str = None, groupby: str = None) -> pl.Expr:
    """将字符串公式转化为pl的表达式格式

    Arguments:
        name {str} -- 名字
        feature {str} -- _description_

    Returns:
        _type_ -- _description_
    """
    # Following patterns will be matched:
    # - $close -> Feature("close")
    # - $close5 -> Feature("close5")
    # - $open+$close -> Feature("open")+Feature("close")
    # TODO: this maybe used in the feature if we want to support the computation of different frequency data
    # - $close@5min -> Feature("close", "5min")

    if feature is None:
        feature = name

    # Chinese punctuation regex:
    # \u3001 -> 、
    # \uff1a -> ：
    # \uff08 -> (
    # \uff09 -> )
    chinese_punctuation_regex = r"\u3001\uff1a\uff08\uff09"
    for pattern, new in [
        (
            rf"\$\$([\w{chinese_punctuation_regex}]+)",
            r'PFeature("\1")',
        ),  # $$ must be before $
        (rf"\$([\w{chinese_punctuation_regex}]+)", r'pl.col("\1")'),
        # (r"(\w+\s*)\(", r"Operators.\1("),
    ]:  # Features  # Operators
        feature = re.sub(pattern, new, feature)

    return (
        eval(feature).alias(name)
        if groupby is None
        else eval(feature).over(groupby).alias(name)
    )


class vxFactorBuilder:
    def __init__(
        self,
        mdapi: vxMdAPI,
        instruments: Union[str, vxInstruments, List] = "cnstocks",
        start_date: DateTimeType = None,
        end_date: DateTimeType = None,
        freq: str = "day",
    ):
        self.start_date = to_datetime(start_date or "2005-01-01")
        self.end_date = to_datetime(end_date or vxtime.today())

        if isinstance(instruments, str):
            instruments = mdapi.instruments(instruments)
        if isinstance(instruments, list):
            instruments = vxInstruments("default").update_components(
                instruments, start_date
            )

        self._mdapi = vxWrapper.init_by_config(mdapi) if mdapi else vxMdAPI()
        self._instruments = instruments
        self._instruments_filter = None
        self._features = self._mdapi.features(
            instruments=self._instruments,
            start_date=self.start_date,
            end_date=self.end_date,
            freq=freq,
        )

        logger.info(f"加载特征数据: {self._features.columns} ")

    def exclude_instruments(
        self, instruments: Union[str, vxInstruments]
    ) -> "vxFactorBuilder":
        """排除股票池中的股票

        Arguments:
            instruments {vxInstruments} -- 股票池

        Returns:
            vxFactorBuilder -- _description_
        """
        if isinstance(instruments, str):
            instruments = self._mdapi.instruments(instruments)

        self._instruments.difference(instruments)
        self._instruments_filter = None
        logger.info(f"剔除股票池: {instruments.name}")
        return self

    @property
    def instruments_filter(self) -> pl.DataFrame:
        """股票池过滤器"""
        if self._instruments_filter is None:
            self._instruments_filter = self.build_instruments_filter()
        return self._instruments_filter

    def build_instruments_filter(self) -> pl.DataFrame:
        """构建股票池过滤器

        Returns:
            pl.DataFrame -- _description_
        """
        trade_dates = self._mdapi.calendar(
            start_date=self.start_date, end_date=self.end_date
        )
        instruments_filters = [
            pl.DataFrame(
                {"symbol": self._instruments.list_instruments(trade_date)}
            ).select(
                pl.lit(trade_date).alias("trade_date"),
                pl.col("symbol"),
                pl.lit(True).alias("mask"),
            )
            for trade_date in tqdm(
                trade_dates, f"构建股票池过滤器{self._instruments.name}"
            )
        ]

        return pl.concat(instruments_filters)

    def build_industry_factor_matrix(self) -> pl.DataFrame:
        """生成行业因子矩阵

        Returns:
            pl.DataFrame -- industry_factor_matrix 行业因子矩阵
        """
        trade_dates = self._mdapi.calendar(
            start_date=self.start_date, end_date=self.end_date
        )

    def build_on_timeseries(self, **factor_exprs: Dict[str, str]) -> "vxFactorBuilder":
        """基于时序构建因子

        Arguments:
            factor_exprs {dict} -- 因子定义表达式如: MA20="Mean($close,20)",EMA20="EMA($close, 20)" ...

        Returns:
            vxFactorBuilder --
        """

        with vxtime.timeit(f"基于时序构建因子: {len(factor_exprs)}"):
            self._features = self._features.with_columns(
                [
                    to_expr(name, factor_expr, groupby="symbol")
                    for name, factor_expr in factor_exprs.items()
                ]
            )

        return self

    def build_on_sectors(self, **factor_exprs: Dict[str, str]) -> "vxFactorBuilder":
        """基于横截面构建因子

        Arguments:
            factor_exprs {dict} -- 因子定义表达式如: MA20="Mean($close,20)",EMA20="EMA($close, 20)" ...

        """
        with vxtime.timeit(f"基于横截面构建因子: {len(factor_exprs)}"):
            self._features = self._features.with_columns(
                [
                    to_expr(name, factor_expr, groupby="trade_date")
                    for name, factor_expr in factor_exprs.items()
                ]
            )

        return self

    def collect(self, *factor_names: List[str]) -> pl.DataFrame:
        if len(factor_names) == 1 and isinstance(factor_names[0], list):
            factor_names = factor_names[0]

        # factor_names = set(factor_names)
        if "trade_date" in factor_names:
            factor_names.remove("trade_date")
        if "symbol" in factor_names:
            factor_names.remove("symbol")

        factor_cols = (
            pl.col("trade_date", "symbol", *factor_names)
            if factor_names
            else pl.col("*")
        )

        # factor_cols = pl.col(factor_names) if factor_names else pl.col("*")

        if isinstance(self._features, pl.LazyFrame):
            with vxtime.timeit("计算因子...", show_title=True):
                features = self._features.collect()
            logger.debug(f"features: {features.tail(5)}")
        else:
            features = self._features

        with vxtime.timeit("过滤股票池..."):
            return (
                self.instruments_filter.join(
                    features, on=["trade_date", "symbol"], how="inner"
                )
                .filter("mask")
                .select(factor_cols)
            )

    def normalize(self, factor_names: List[str]) -> "vxFactorBuilder":
        """标准化"""


if __name__ == "__main__":
    import alphalens

    mdapi = vxMdAPI()
    cnstocks = mdapi.instruments("cnstocks")
    f = mdapi.features(cnstocks, "2005-01-01", "2023-3-01")
    print(f.groupby("is_trading").count())
    vxtime.sleep(2)

    fbuilder = vxFactorBuilder(mdapi, cnstocks, "2005-01-04", "2023-03-01")

    # print(fbuilder._instruments_filter.filter(pl.col("mask")))
    # fbuilder.exclude_instruments("newstock")
    # print(fbuilder._instruments_filter.filter(pl.col("mask")))
    fbuilder.build_on_timeseries(
        STO="1/MA($turnover_rate,21)+1/MA($turnover_rate,63)+1/MA($turnover_rate,63*4)",
        VMOM="MA( $close / Ref($close,1) / $turnover_rate, 21)",
        # MA20="EMA($close,20)",
    )
    factor_data = fbuilder.collect("is_trading", "STO", "VMOM")
    factor_data.drop_nulls().write_csv("./dist/factor.csv")
    factor_data = (
        factor_data.drop_nulls().select(["trade_date", "symbol", "STO"]).to_pandas()
    )
    factor_data = factor_data.set_index(["trade_date", "symbol"])
    print(factor_data)
    # print(factor_data.filter(pl.col("STO").is_not_null()))
    prices = fbuilder.collect("open").to_pandas()
    prices = prices.set_index(["trade_date"])
    print(prices.unstack())
    # data = alphalens.utils.get_clean_factor_and_forward_returns(
    #    factor=factor_data, prices=prices, quantiles=5, periods=(1, 5, 20)
    # )
    # print(data)
