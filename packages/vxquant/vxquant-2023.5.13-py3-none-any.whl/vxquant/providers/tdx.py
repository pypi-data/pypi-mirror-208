"""tdx行情"""

import time
from enum import Enum
from contextlib import suppress

from typing import List, Dict
from queue import PriorityQueue
from multiprocessing import Lock
from functools import reduce
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from vxutils import logger, vxtime, diskcache
from vxquant.model.exchange import vxTick
from vxquant.model.nomalize import to_symbol
from vxquant.model.typehint import InstrumentType
from vxquant.model.tools.tdxData import tdxTickConvter
from vxquant.providers.base import vxHQProvider

try:
    from pytdx.hq import TdxHq_API, TDXParams
    from pytdx.config.hosts import hq_hosts
except ImportError as e:
    raise ImportError("pytdx包未安装，请运行: pip install pytdx 安装。") from e

__TDXHOSTS__ = "__TDXHOSTS__"


class TDXExchange(Enum):
    """通达信市场转换"""

    SHSE = TDXParams.MARKET_SH
    SZSE = TDXParams.MARKET_SZ
    BJSE = 2


def to_tdx_symbol(symbol):
    """转成tdx的symbol格式: (market,code)

    Arguments:
        symbol {_type_} -- symbol
    """
    market, code = to_symbol(symbol).split(".")
    return (TDXExchange[market].value, code)


def parser_tdx_symbol(market, code):
    """将tdx的symbol格式转化成symbol："SHSE.0000001"

    Arguments:
        market {_type_} -- tdx 的market代码
        code {_type_} -- 证券代码
    """
    return f"{TDXExchange(market).name}.{code}"


class TdxHq_APIPool:
    """tdx行情接口池"""

    _hosts = PriorityQueue()
    _apis = PriorityQueue()
    _lock = Lock()

    def __init__(self):
        # self._cost = None
        self._api = None
        with self._lock:
            self.reflash_hosts()

    @classmethod
    def reflash_hosts(cls) -> None:
        if cls._hosts.qsize() >= 10:
            return

        cls._hosts.queue.clear()

        data = diskcache.get(__TDXHOSTS__, [])

        if len(data) == 0 or not isinstance(data, list):
            tdxapi = TdxHq_API()
            pbar = tqdm(hq_hosts)
            data = []
            for server_name, host, port in pbar:
                pbar.set_description(f"tdx连通性测试 {server_name}: {host}@{port}...")
                start = time.perf_counter()
                with suppress(TimeoutError):
                    if tdxapi.connect(host, port, time_out=1):
                        cost = (time.perf_counter() - start) * 1000
                        tdxapi.disconnect()
                        data.append((cost, host, port))

            if data:
                diskcache.set(__TDXHOSTS__, data, expired_dt=vxtime.today("23:59:59"))

        [cls._hosts.put(item) for item in data]

    def __enter__(self):
        with self._lock:
            self.reflash_hosts()

        while self._apis.qsize() > 0:
            lastconnect_dt, self._api = self._apis.get_nowait()
            if (lastconnect_dt + 60 < vxtime.now()) or (self._api.do_heartbeat()):
                return self._api

        while not self._hosts.empty():
            cost, host, port = self._hosts.get_nowait()
            try:
                self._api = TdxHq_API()
                if self._api.connect(host, port, time_out=0.7):
                    return self._api
            except Exception as e:
                logger.info(f"连接至:{host}:{port} 发生错误: {e}", exc_info=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None or self._api.do_heartbeat():
            self._apis.put_nowait((vxtime.now(), self._api))


class TdxHQProvider(vxHQProvider):
    def _hq(self, *symbols: List[InstrumentType]) -> Dict[InstrumentType, vxTick]:
        if len(symbols) == 1 and isinstance(symbols[0], list):
            symbols = symbols[0]

        if not symbols:
            return {}

        tdxsymbols = [to_tdx_symbol(symbol) for symbol in symbols]
        results = {}

        with TdxHq_APIPool() as api:
            missing_tdxsymbols = []
            for i in range(0, len(tdxsymbols), 80):
                data = api.get_security_quotes(tdxsymbols[i : i + 80])
                if data and len(data) == len(tdxsymbols[i : i + 80]):
                    results.update(map(lambda x: tdxTickConvter(x, key="symbol"), data))
                else:
                    missing_tdxsymbols.append(tdxsymbols[i : i + 80])
            if missing_tdxsymbols:
                vxtime.sleep(0.1)
                for symbol in missing_tdxsymbols:
                    data = api.get_security_quotes([symbol])
                    if data:
                        results.update(
                            map(lambda x: tdxTickConvter(x, key="symbol"), data)
                        )
        return results


class MultiTdxHQProvider(vxHQProvider):
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(5)

    def _hq(self, *symbols: List[InstrumentType]) -> Dict[InstrumentType, vxTick]:
        if len(symbols) == 1 and isinstance(symbols[0], list):
            symbols = symbols[0]

        if not symbols:
            return {}

        cnt = len(symbols) // (80 * 5) + 1
        rets = [
            self._executor.submit(
                self._tdx_get_security_quotes, symbols[i : i + 80 * cnt]
            )
            for i in range(0, len(symbols), 80 * cnt)
        ]

        def _r(x, y):
            x.update(y.result())
            return x

        return reduce(_r, as_completed(rets), {})

    def _tdx_get_security_quotes(
        self, symbols: List[InstrumentType]
    ) -> Dict[InstrumentType, vxTick]:
        tdxsymbols = [to_tdx_symbol(symbol) for symbol in symbols]
        results = {}
        missing_tdxsymbols = []

        with TdxHq_APIPool() as api:
            for i in range(0, len(tdxsymbols), 80):
                data = api.get_security_quotes(tdxsymbols[i : i + 80])
                if data and len(data) == len(tdxsymbols[i : i + 80]):
                    results.update(map(lambda x: tdxTickConvter(x, key="symbol"), data))
                else:
                    missing_tdxsymbols.extend(tdxsymbols[i : i + 80])
            if missing_tdxsymbols:
                vxtime.sleep(0.1)
                for symbol in missing_tdxsymbols:
                    data = api.get_security_quotes([symbol])
                    if data:
                        results.update(
                            map(lambda x: tdxTickConvter(x, key="symbol"), data)
                        )

        return results


if __name__ == "__main__":
    from vxutils import to_datetime

    with TdxHq_APIPool() as tdxapi:
        print("hello world")

    with vxtime.timeit("create hqapi"):
        hq_api = MultiTdxHQProvider()

    # print(diskcache.get("__suspend_symbols__"))

    symbols = [
        "SHSE.110043",
        "SHSE.110044",
        "SHSE.110045",
        "SHSE.110047",
        "SHSE.110048",
        "SHSE.110052",
        "SHSE.110053",
        "SHSE.110055",
        "SHSE.110057",
        "SHSE.110058",
        "SHSE.110059",
        "SHSE.110060",
        "SHSE.110061",
        "SHSE.110062",
        "SHSE.110063",
        "SHSE.110064",
        "SHSE.110067",
        "SHSE.110068",
        "SHSE.110070",
        "SHSE.110072",
        "SHSE.110073",
        "SHSE.110074",
        "SHSE.110075",
        "SHSE.110076",
        "SHSE.110077",
        "SHSE.110079",
        "SHSE.110080",
        "SHSE.110081",
        "SHSE.110082",
        "SHSE.110083",
        "SHSE.110084",
        "SHSE.110085",
        "SHSE.110086",
        "SHSE.110087",
        "SHSE.110088",
        "SHSE.110089",
        "SHSE.110090",
        "SHSE.110091",
        "SHSE.110092",
        "SHSE.111000",
        "SHSE.111001",
        "SHSE.111002",
        "SHSE.111003",
        "SHSE.111004",
        "SHSE.111005",
        "SHSE.111006",
        "SHSE.111007",
        "SHSE.111008",
        "SHSE.111009",
        "SHSE.111010",
        "SHSE.111011",
        "SHSE.111012",
        "SHSE.113011",
        "SHSE.113013",
        "SHSE.113016",
        "SHSE.113017",
        "SHSE.113021",
        "SHSE.113024",
        "SHSE.113025",
        "SHSE.113027",
        "SHSE.113030",
        "SHSE.113033",
        "SHSE.113037",
        "SHSE.113039",
        "SHSE.113042",
        "SHSE.113043",
        "SHSE.113044",
        "SHSE.113045",
        "SHSE.113046",
        "SHSE.113047",
        "SHSE.113048",
        "SHSE.113049",
        "SHSE.113050",
        "SHSE.113051",
        "SHSE.113052",
        "SHSE.113053",
        "SHSE.113054",
        "SHSE.113055",
        "SHSE.113056",
        "SHSE.113057",
        "SHSE.113058",
        "SHSE.113059",
        "SHSE.113060",
        "SHSE.113061",
        "SHSE.113062",
        "SHSE.113063",
        "SHSE.113064",
        "SHSE.113065",
        "SHSE.113504",
        "SHSE.113505",
        "SHSE.113516",
        "SHSE.113519",
        "SHSE.113524",
        "SHSE.113526",
        "SHSE.113527",
        "SHSE.113530",
        "SHSE.113532",
        "SHSE.113534",
        "SHSE.113535",
        "SHSE.113537",
        "SHSE.113542",
        "SHSE.113545",
        "SHSE.113546",
        "SHSE.113549",
        "SHSE.113561",
        "SHSE.113563",
        "SHSE.113565",
        "SHSE.113566",
        "SHSE.113567",
        "SHSE.113569",
        "SHSE.113570",
        "SHSE.113573",
        "SHSE.113574",
        "SHSE.113575",
        "SHSE.113576",
        "SHSE.113577",
        "SHSE.113578",
        "SHSE.113579",
        "SHSE.113582",
        "SHSE.113584",
        "SHSE.113585",
        "SHSE.113588",
        "SHSE.113589",
        "SHSE.113591",
        "SHSE.113593",
        "SHSE.113594",
        "SHSE.113595",
        "SHSE.113596",
        "SHSE.113597",
        "SHSE.113598",
        "SHSE.113600",
        "SHSE.113601",
        "SHSE.113602",
        "SHSE.113604",
        "SHSE.113605",
        "SHSE.113606",
        "SHSE.113608",
        "SHSE.113609",
        "SHSE.113610",
        "SHSE.113615",
        "SHSE.113616",
        "SHSE.113618",
        "SHSE.113619",
        "SHSE.113621",
        "SHSE.113622",
        "SHSE.113623",
        "SHSE.113624",
        "SHSE.113625",
        "SHSE.113626",
        "SHSE.113627",
        "SHSE.113628",
        "SHSE.113629",
        "SHSE.113631",
        "SHSE.113632",
        "SHSE.113633",
        "SHSE.113634",
        "SHSE.113636",
        "SHSE.113637",
        "SHSE.113638",
        "SHSE.113639",
        "SHSE.113640",
        "SHSE.113641",
        "SHSE.113643",
        "SHSE.113644",
        "SHSE.113646",
        "SHSE.113647",
        "SHSE.113648",
        "SHSE.113649",
        "SHSE.113650",
        "SHSE.113651",
        "SHSE.113652",
        "SHSE.113653",
        "SHSE.113654",
        "SHSE.113655",
        "SHSE.113656",
        "SHSE.113657",
        "SHSE.113658",
        "SHSE.113659",
        "SHSE.113660",
        "SHSE.113661",
        "SHSE.113662",
        "SHSE.113663",
        "SHSE.113664",
        "SHSE.113665",
        "SHSE.118000",
        "SHSE.118003",
        "SHSE.118004",
        "SHSE.118005",
        "SHSE.118006",
        "SHSE.118007",
        "SHSE.118008",
        "SHSE.118009",
        "SHSE.118010",
        "SHSE.118011",
        "SHSE.118012",
        "SHSE.118013",
        "SHSE.118014",
        "SHSE.118015",
        "SHSE.118016",
        "SHSE.118017",
        "SHSE.118018",
        "SHSE.118019",
        "SHSE.118020",
        "SHSE.118021",
        "SHSE.118022",
        "SHSE.118023",
        "SHSE.118024",
        "SHSE.118025",
        "SHSE.118026",
        "SHSE.118027",
        "SHSE.118028",
        "SHSE.118029",
        "SHSE.118030",
        "SZSE.123002",
        "SZSE.123004",
        "SZSE.123010",
        "SZSE.123011",
        "SZSE.123012",
        "SZSE.123013",
        "SZSE.123014",
        "SZSE.123015",
        "SZSE.123018",
        "SZSE.123022",
        "SZSE.123025",
        "SZSE.123031",
        "SZSE.123034",
        "SZSE.123035",
        "SZSE.123038",
        "SZSE.123039",
        "SZSE.123044",
        "SZSE.123046",
        "SZSE.123048",
        "SZSE.123049",
        "SZSE.123050",
        "SZSE.123052",
        "SZSE.123054",
        "SZSE.123056",
        "SZSE.123057",
        "SZSE.123059",
        "SZSE.123061",
        "SZSE.123063",
        "SZSE.123064",
        "SZSE.123065",
        "SZSE.123067",
        "SZSE.123071",
        "SZSE.123072",
        "SZSE.123075",
        "SZSE.123076",
        "SZSE.123077",
        "SZSE.123078",
        "SZSE.123080",
        "SZSE.123082",
        "SZSE.123083",
        "SZSE.123085",
        "SZSE.123087",
        "SZSE.123088",
        "SZSE.123089",
        "SZSE.123090",
        "SZSE.123091",
        "SZSE.123092",
        "SZSE.123093",
        "SZSE.123096",
        "SZSE.123098",
        "SZSE.123099",
        "SZSE.123100",
        "SZSE.123101",
        "SZSE.123103",
        "SZSE.123104",
        "SZSE.123105",
        "SZSE.123106",
        "SZSE.123107",
        "SZSE.123108",
        "SZSE.123109",
        "SZSE.123112",
        "SZSE.123113",
        "SZSE.123114",
        "SZSE.123115",
        "SZSE.123116",
        "SZSE.123117",
        "SZSE.123118",
        "SZSE.123119",
        "SZSE.123120",
        "SZSE.123121",
        "SZSE.123122",
        "SZSE.123124",
        "SZSE.123126",
        "SZSE.123127",
        "SZSE.123128",
        "SZSE.123129",
        "SZSE.123130",
        "SZSE.123131",
        "SZSE.123132",
        "SZSE.123133",
        "SZSE.123134",
        "SZSE.123135",
        "SZSE.123136",
        "SZSE.123138",
        "SZSE.123140",
        "SZSE.123141",
        "SZSE.123142",
        "SZSE.123143",
        "SZSE.123144",
        "SZSE.123145",
        "SZSE.123146",
        "SZSE.123147",
        "SZSE.123148",
        "SZSE.123149",
        "SZSE.123150",
        "SZSE.123151",
        "SZSE.123152",
        "SZSE.123153",
        "SZSE.123154",
        "SZSE.123155",
        "SZSE.123156",
        "SZSE.123157",
        "SZSE.123158",
        "SZSE.123159",
        "SZSE.123160",
        "SZSE.123161",
        "SZSE.123162",
        "SZSE.123163",
        "SZSE.123164",
        "SZSE.123165",
        "SZSE.123166",
        "SZSE.123167",
        "SZSE.123168",
        "SZSE.123169",
        "SZSE.123170",
        "SZSE.123171",
        "SZSE.123172",
        "SZSE.123173",
        "SZSE.127004",
        "SZSE.127005",
        "SZSE.127006",
        "SZSE.127007",
        "SZSE.127012",
        "SZSE.127014",
        "SZSE.127015",
        "SZSE.127016",
        "SZSE.127017",
        "SZSE.127018",
        "SZSE.127019",
        "SZSE.127020",
        "SZSE.127021",
        "SZSE.127022",
        "SZSE.127024",
        "SZSE.127025",
        "SZSE.127026",
        "SZSE.127027",
        "SZSE.127028",
        "SZSE.127029",
        "SZSE.127030",
        "SZSE.127031",
        "SZSE.127032",
        "SZSE.127033",
        "SZSE.127034",
        "SZSE.127035",
        "SZSE.127036",
        "SZSE.127037",
        "SZSE.127038",
        "SZSE.127039",
        "SZSE.127040",
        "SZSE.127041",
        "SZSE.127042",
        "SZSE.127043",
        "SZSE.127044",
        "SZSE.127045",
        "SZSE.127046",
        "SZSE.127047",
        "SZSE.127049",
        "SZSE.127050",
        "SZSE.127051",
        "SZSE.127052",
        "SZSE.127053",
        "SZSE.127054",
        "SZSE.127055",
        "SZSE.127056",
        "SZSE.127057",
        "SZSE.127058",
        "SZSE.127059",
        "SZSE.127060",
        "SZSE.127061",
        "SZSE.127062",
        "SZSE.127063",
        "SZSE.127064",
        "SZSE.127065",
        "SZSE.127066",
        "SZSE.127067",
        "SZSE.127068",
        "SZSE.127069",
        "SZSE.127070",
        "SZSE.127071",
        "SZSE.127072",
        "SZSE.127073",
        "SZSE.127074",
        "SZSE.127075",
        "SZSE.127076",
        "SZSE.127077",
        "SZSE.127078",
        "SZSE.127079",
        "SZSE.127080",
        "SZSE.128014",
        "SZSE.128017",
        "SZSE.128021",
        "SZSE.128023",
        "SZSE.128025",
        "SZSE.128026",
        "SZSE.128030",
        "SZSE.128033",
        "SZSE.128034",
        "SZSE.128035",
        "SZSE.128036",
        "SZSE.128037",
        "SZSE.128039",
        "SZSE.128040",
        "SZSE.128041",
        "SZSE.128042",
        "SZSE.128044",
        "SZSE.128048",
        "SZSE.128049",
        "SZSE.128053",
        "SZSE.128056",
        "SZSE.128062",
        "SZSE.128063",
        "SZSE.128066",
        "SZSE.128070",
        "SZSE.128071",
        "SZSE.128072",
        "SZSE.128074",
        "SZSE.128075",
        "SZSE.128076",
        "SZSE.128078",
        "SZSE.128079",
        "SZSE.128081",
        "SZSE.128082",
        "SZSE.128083",
        "SZSE.128085",
        "SZSE.128087",
        "SZSE.128090",
        "SZSE.128091",
        "SZSE.128095",
        "SZSE.128097",
        "SZSE.128100",
        "SZSE.128101",
        "SZSE.128105",
        "SZSE.128106",
        "SZSE.128108",
        "SZSE.128109",
        "SZSE.128111",
        "SZSE.128114",
        "SZSE.128116",
        "SZSE.128117",
        "SZSE.128118",
        "SZSE.128119",
        "SZSE.128120",
        "SZSE.128121",
        "SZSE.128122",
        "SZSE.128123",
        "SZSE.128124",
        "SZSE.128125",
        "SZSE.128127",
        "SZSE.128128",
        "SZSE.128129",
        "SZSE.128130",
        "SZSE.128131",
        "SZSE.128132",
        "SZSE.128133",
        "SZSE.128134",
        "SZSE.128135",
        "SZSE.128136",
        "SZSE.128137",
        "SZSE.128138",
        "SZSE.128140",
        "SZSE.128141",
        "SZSE.128142",
        "SZSE.128143",
        "SZSE.128144",
        "SZSE.128145",
    ]
    with vxtime.timeit():
        data = hq_api(
            # "SHSE.399001",
            "SHSE.600000",
            "SZSE.000001",
            "SHSE.000001",
            "SHSE.000688",
            "SHSE.511880",
            "SHSE.510300",
            "SHSE.511990",
            "SHSE.511660",
            "SHSE.204001",
            "SZSE.399001",
            "SZSE.399673",
            "SZSE.159001",
            "SZSE.159919",
            "SZSE.159915",
            "SZSE.159937",
            "SZSE.131810",
            # *symbols,
        )
        # for symbol, tick in data.items():
        #    print(f"{symbol} == {(tick.lasttrade/tick.yclose-1)*100:,.2f}%")
        print(len(set(symbols)), len(data))

    with vxtime.timeit():
        data = hq_api(symbols)
        print(len(set(symbols)), len(data))

    import polars as pl

    df = pl.DataFrame([tick.message for tick in data.values()]).with_columns(
        [pl.col(["created_dt", "updated_dt"]).apply(to_datetime)]
    )
    print(df)
