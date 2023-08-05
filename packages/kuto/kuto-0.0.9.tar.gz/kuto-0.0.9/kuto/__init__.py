from kuto.case import TestCase, Page
from kuto.core.api.request import HttpReq
from kuto.core.android.element import AdrElem
from kuto.core.ios.element import IosElem
from kuto.core.web.selenium_element import SeleElem
from kuto.core.web.selenium_driver import (
    ChromeConfig,
    FirefoxConfig,
    IEConfig,
    EdgeConfig,
    SafariConfig
)
from kuto.running.runner import main
from kuto.utils.config import config
from kuto.utils.decorate import *
from kuto.utils.log import logger


__version__ = "0.0.9"
__description__ = "移动、web、接口自动化测试框架"
