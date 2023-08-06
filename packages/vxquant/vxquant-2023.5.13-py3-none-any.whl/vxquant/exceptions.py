"""账户异常类"""


__all__ = []


class vxQuantException(Exception):
    pass


class RiskRuleCheckFailed(vxQuantException):
    # 不符合风控规则
    pass


class NoEnoughCash(vxQuantException):
    # 资金不足
    pass


class NoEnoughPosition(vxQuantException):
    pass


class IllegalAccountId(vxQuantException):
    # 非法账户ID
    pass


class IllegalStrategyId(vxQuantException):
    # 非法策略ID
    pass


class IllegalSymbol(vxQuantException):
    # 非法交易标的
    pass


class IllegalVolume(vxQuantException):
    # 非法委托量
    pass


class IllegalPrice(vxQuantException):
    # 非法委托价
    pass


class AccountDisabled(vxQuantException):
    # 交易账号被禁止交易
    pass


class AccountDisconnected(vxQuantException):
    # 交易账号未连接
    pass


class AccountLoggedout(vxQuantException):
    # 交易账号未登录
    pass


class NotInTradingSession(vxQuantException):
    # 非交易时段
    pass


class OrderTypeNotSupported(vxQuantException):
    # 委托类型不支持
    pass


class Throttle(vxQuantException):
    # 流控限制
    pass


class IllegalOrder(vxQuantException):
    # 交易委托不支持
    pass


class OrderFinalized(vxQuantException):
    # 委托已经完成
    pass


class UnknownOrder(vxQuantException):
    # 未知委托
    pass


class AlreadyInPendingCancel(vxQuantException):
    # 已经在撤单中
    pass
