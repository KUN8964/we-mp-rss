from core.config import cfg
from core.wx_service import get_wx_cfg as _get_wx_cfg

wx_cfg = _get_wx_cfg()
import urllib3
urllib3.disable_warnings()