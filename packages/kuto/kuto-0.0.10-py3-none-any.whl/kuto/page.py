import time
from typing import Union

from kuto.core.h5.driver import H5Driver
from kuto.core.web.selenium_driver import WebDriver
from kuto.core.ios.driver import IosDriver
from kuto.core.android.driver import AndroidDriver
from kuto.utils.log import logger
# from kuto.core.android.element import AdrElem
# from kuto.core.ios.element import IosElem
# from kuto.core.web.element import WebElem
# from kuto.core.screenshot.element import ImageElem
# from kuto.core.ocr.element import OCRElem
from kuto.utils.exceptions import NoSuchDriverType


# def Elem(
#         driver: Union[AndroidDriver, IosDriver, WebDriver] = None,
#         res_id: str = None,
#         class_name: str = None,
#         text: str = None,
#         name: str = None,
#         label: str = None,
#         value: str = None,
#         id_: str = None,
#         link_text: str = None,
#         partial_link_text: str = None,
#         tag_name: str = None,
#         css: str = None,
#         screenshot: str = None,
#         ocr: str = None,
#         xpath: str = None,
#         index: int = None,
#         desc: str = None
# ):
#     _kwargs = {}
#     if res_id is not None:
#         _kwargs["res_id"] = res_id
#     if class_name is not None:
#         _kwargs["class_name"] = class_name
#     if text is not None:
#         _kwargs["text"] = text
#     if name is not None:
#         _kwargs["name"] = name
#     if label is not None:
#         _kwargs["label"] = label
#     if value is not None:
#         _kwargs["value"] = value
#     if id_ is not None:
#         _kwargs["id_"] = id_
#     if link_text is not None:
#         _kwargs["link_text"] = link_text
#     if partial_link_text is not None:
#         _kwargs["partial_link_text"] = partial_link_text
#     if tag_name is not None:
#         _kwargs["tag_name"] = tag_name
#     if css is not None:
#         _kwargs["css"] = css
#     if xpath is not None:
#         _kwargs["xpath"] = xpath
#     if index is not None:
#         _kwargs["index"] = index
#     if screenshot is not None:
#         _kwargs["screenshot"] = screenshot
#     if ocr is not None:
#         _kwargs["ocr"] = ocr
#     if desc is None:
#         raise ElementNameEmptyException("请设置控件名称")
#     else:
#         _kwargs["desc"] = desc
#     return _kwargs


class Page(object):
    """页面基类，用于pom模式封装"""

    def __init__(self, driver: Union[AndroidDriver, IosDriver, WebDriver, H5Driver]):
        self.driver = driver

    @staticmethod
    def sleep(n):
        """休眠"""
        logger.info(f"休眠 {n} 秒")
        time.sleep(n)

    @staticmethod
    def open(self, url):
        if not isinstance(self.driver, WebDriver):
            raise NoSuchDriverType("不是webdriver，不支持")
        self.driver.open_url(url)

    # def elem(self, kwargs):
    #     """封装安卓、ios、web元素"""
    #     if isinstance(self.driver, AndroidDriver):
    #         return AdrElem(self.driver, **kwargs)
    #     elif isinstance(self.driver, IosDriver):
    #         return IosElem(self.driver, **kwargs)
    #     elif isinstance(self.driver, WebDriver):
    #         return WebElem(self.driver, **kwargs)
    #     else:
    #         raise NoSuchDriverType('不支持的驱动类型')
