from vxutils import logger
from .base import vxCommand, vxQuantCommand, vxInitDirCommand
from vxsched import vxscheduler

_default_config = {"params": {}, "settings": {}}



__all___ = ["vxCommand", "vxQuantCommand", "vxInitDirCommand"]

try:
    from .gmagent import run_gmagent, run_debug_gmagent, _gmagent_config

#    vxQuantCommand("gm", run_gmagent, _gmagent_config)
#    vxQuantCommand("gmdebug", run_debug_gmagent, _gmagent_config)
except ImportError as e:
    logger.info(f"导入gmagent错误，: {e}")

try:
    from .qmtagent import run_miniqmtagent, _qmtagent_config, run_debug_miniagent

#    vxQuantCommand("qmt", run_miniqmtagent, _qmtagent_config)
#    vxQuantCommand("qmtdebug", run_debug_miniagent, _qmtagent_config)
except ImportError as e:
    logger.info(f"导入miniqmtagent错误，: {e}")
