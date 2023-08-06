"""数据指标计算器"""
import re
import abc
from vxutils import vxtime
from vxdataset.expr.ops import *
from typing import Callable, Any
from tdqm import tdqm


class vxDataHandler(abc.ABC):
    def __init__(self, loader):
        self._loader = loader
        self._datas = None

    @classmethod
    def from_dataloader(
        cls, loader: Callable, symbols: str, start_date: Any, end_date: Any
    ):
        return cls(loader(symbols, start_date, end_date))

    def _parser_expr(self, name, feature):
        # Following patterns will be matched:
        # - $close -> Feature("close")
        # - $close5 -> Feature("close5")
        # - $open+$close -> Feature("open")+Feature("close")
        # TODO: this maybe used in the feature if we want to support the computation of different frequency data
        # - $close@5min -> Feature("close", "5min")

        if not isinstance(feature, str):
            feature = str(feature)
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
            (rf"\$([\w{chinese_punctuation_regex}]+)", r'Feature("\1")'),
            # (r"(\w+\s*)\(", r"Operators.\1("),
        ]:  # Features  # Operators
            feature = re.sub(pattern, new, feature)

        return eval(feature).over("symbol").alias(name)

    def _handle(self, data, exprs):
        return data.with_columns(exprs)

    def calc_features(self, features):
        exprs = [self._parser_expr(name, feature) for name, feature in features.items()]

        with vxtime.timeit("build features"):
            self._datas = list(
                map(lambda x: self._handle(x, exprs), self._datas.values())
            )

        return self

    def to_pandas(self):
        return self._datas.to_pandas()

    def to_polars(self):
        return self._datas

    def to_csv(self, filename):
        with open(filename, "w") as f:
            self._datas.write_csv(f)


if __name__ == "__main__":
    from vxdataset.loaders.csv import vxCSVLoader

    loader = vxCSVLoader("examples/data/")
    d = loader.load(["sh000300"])

    features = {
        "high": "$high",
        "mom20": "Ref($close, 20)/$close",
        "ret": "$close/Ref($close,1)-1",
        "roc20": "Rank($high,252)",
    }
    handler = vxDataHandler(loader)
    ds = handler.calc_features(features)
    print(ds)
