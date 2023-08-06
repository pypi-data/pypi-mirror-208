"""因子标准化"""

import polars as pl
from tqdm import tqdm
from typing import List, Any, Union
from scipy.stats import linregress
from concurrent.futures import ThreadPoolExecutor as Executor
from vxutils import vxtime


def filter_extreme_mad(
    factor_col: Union[pl.Expr, pl.Series], n: int = 3
) -> Union[pl.Expr, pl.Series]:
    """MAD 法去极值

    Arguments:
        factor_col {Union[pl.Expr, pl.Series]} -- factor
        n {int} -- 区间系数

    Returns:
        Union[pl.Expr, pl.Series] -- 去极值后的factor
    """

    new_median = (factor_col - factor_col.median()).abs().median()
    downlimit = factor_col.median() - n * new_median
    uplimit = factor_col.median() + n * new_median
    return (
        pl.when(factor_col < downlimit)
        .then(downlimit)
        .otherwise(pl.when(factor_col > uplimit).then(uplimit).otherwise(factor_col))
    )


def filter_extreme_winsorize_std(
    factor_col: Union[pl.Expr, pl.Series], n: int = 3
) -> pl.Expr:
    """winsorize_std法 去极值

    Arguments:
        factor_col {Union[pl.Expr, pl.Series]} -- factor
        n {int} -- 区间系数

    Returns:
        Union[pl.Expr, pl.Series] -- 去极值后的factor
    """

    return (
        pl.when(factor_col < (factor_col.mean() - n * factor_col.std()))
        .then(factor_col.mean() - n * factor_col.std())
        .otherwise(
            pl.when(factor_col > (factor_col.mean() + n * factor_col.std()))
            .then(factor_col.mean() + n * factor_col.std())
            .otherwise(factor_col)
        )
    )


class vxNeutralize:
    def __init__(self, neutralize_factors: pl.DataFrame) -> None:
        self._neutralize_factors = neutralize_factors

    def __call__(self, factor: pl.Series) -> pl.Series:
        pass


def neutralize(
    factor: pl.Series, neutralize_factors: pl.DataFrame, pbar: tqdm
) -> pl.Series:
    """中性化

    Arguments:
        factor {pl.Series} -- 待中性化的因子
        neutralize_factors {pl.DataFrame} -- 中性化因子s

    Returns:
        pl.Series -- 中性化后因子
    """


class vxFactorNormalizer:
    def __init__(
        self,
        filter_extreme_method: str = "mad",
        N: int = 3,
    ):
        if filter_extreme_method == "mad":
            self._filter_extreme_method = filter_extreme_mad
        else:
            self._filter_extreme_method = filter_extreme_winsorize_std
        self._n = N

    def __call__(self, factors: pl.DataFrame, factor_names: List[str]) -> pl.DataFrame:
        factor_names = list(set(factor_names) - {"trade_date", "symbol", "mask"})
        with vxtime.timeit(f"normalizing factors{factor_names}"):
            return (
                factors.fill_nan(None)
                .drop_nulls()
                .with_columns(
                    [
                        self._filter_extreme_method(pl.col(factor_name), self._n).over(
                            "trade_date"
                        )
                        for factor_name in factor_names
                    ]
                )
                .with_columns(
                    [
                        (
                            (pl.col(factor_name) - pl.col(factor_name).mean())
                            / (pl.col(factor_name).std() + 0.000000001)
                        ).over("trade_date")
                        for factor_name in factor_names
                    ]
                )
            )


if __name__ == "__main__":
    factor_data = pl.read_csv("./dist/factor.csv")
    # factor_data = factor_data.fill_nan(0)
    print(factor_data)
    # print(factor_data.filter(pl.col("VMOM").drop_nans()))
    # vmom = factor_data["VMOM"]
    # m = (vmom - vmom.median()).abs().median()
    # print(vmom.clip(vmom.median() - 3 * m, vmom.median() + 3 * m))
    normalizer = vxFactorNormalizer()
    with vxtime.timeit():
        factor_data = normalizer(factor_data, ["STO", "VMOM"])
        print(factor_data)
    # factor_data.filter(pl.col("VMOM").is_nan()).write_csv("dist/null.csv")
    # neutralize_factors = factor_data.select(["trade_date", "symbol", "amount"])
    # normalizer.neutralization(["STO"], neutralize_factors)
    # print(normalizer._factors)
