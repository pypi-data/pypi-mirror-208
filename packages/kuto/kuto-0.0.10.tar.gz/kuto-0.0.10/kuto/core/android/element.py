import inspect
import typing

from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector

from kuto.core.android.driver import AndroidDriver
from kuto.utils.exceptions import NoSuchElementException
from kuto.utils.log import logger
from kuto.utils.config import config


class AdrElem(object):
    """
    安卓元素定义
    """

    def __init__(self,
                 driver: AndroidDriver = None,
                 resourceId: str = None,
                 className: str = None,
                 text: str = None,
                 xpath: str = None,
                 index: int = 0):
        """
        @param driver: 安卓驱动，必填
        @param resourceId: resourceId定位
        @param className: className定位
        @param text: text定位
        @param xpath: xpath定位
        @param index: 定位出多个元素时，指定索引
        """
        self._driver = driver

        self._kwargs = {}
        if resourceId is not None:
            self._kwargs["resourceId"] = resourceId
        if className is not None:
            self._kwargs["className"] = className
        if text is not None:
            self._kwargs["text"] = text

        self._xpath = xpath
        self._index = index

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # def error_handler(self):
    #     """异常处理，暂时只支持resourceId和text"""
    #     errors = config.get_app('errors')
    #     if errors:
    #         logger.info(f'deal errors: {errors}')
    #         for error in errors:
    #             self._driver.d(**error).click_exists()

    # def find_element(self, retry=3, timeout=3):
    #     """
    #     为了留出异常处理的逻辑，所以加了一个find_element的方法，不然可以合并到get_element方法
    #     @param retry: 重试次数
    #     @param timeout: 每次查找时间
    #     @return:
    #     """
    #     if self._xpath is not None:
    #         logger.info(f'find: xpath={self._xpath}')
    #     else:
    #         logger.info(f'find: {self._kwargs}[{self._index}]')
    #     _element = self._driver.d.xpath(self._xpath) if \
    #         self._xpath is not None else self._driver.d(**self._kwargs)[self._index]
    #     while not _element.wait(timeout=timeout):
    #         if retry > 0:
    #             retry -= 1
    #             # self.error_handler()
    #             logger.warning(f'retry： {self._kwargs},{self._index}')
    #         else:
    #             frame = inspect.currentframe().f_back
    #             caller = inspect.getframeinfo(frame)
    #             logger.warning(f'【{caller.function}:{caller.lineno}】find not {self._kwargs}')
    #             return None
    #     return _element

    def get_element(self, timeout=5):
        """
        增加截图的方法
        @param timeout: 每次查找时间
        @return:
        """
        if self._xpath is not None:
            logger.info(f'find: xpath={self._xpath}')
        else:
            logger.info(f'find: {self._kwargs}[{self._index}]')
        _element = self._driver.d.xpath(self._xpath) if \
            self._xpath is not None else self._driver.d(**self._kwargs)[self._index]

        if _element.wait(timeout=timeout):
            return _element
        else:
            self._driver.screenshot("loc_fail")
            raise NoSuchElementException(f"[elem {self._kwargs} loc fail]")

    @property
    def info(self):
        logger.info(f"get info")
        return self.get_element(timeout=1).info

    @property
    def text(self):
        logger.info(f"get text")
        return self.get_element().info.get("text")

    @property
    def bounds(self):
        logger.info(f"get bounds")
        return self.get_element().info.get("bounds")

    def exists(self, timeout=3):
        logger.info(f"if exists")
        try:
            self.get_element(timeout=timeout)
        except:
            return False
        else:
            return True

    @staticmethod
    def _adapt_center(e: typing.Union[UiObject, XPathSelector], offset=(0.5, 0.5)):
        if isinstance(e, UiObject):
            return e.center(offset=offset)
        else:
            return e.offset(offset[0], offset[1])

    def click(self):
        logger.info("click")
        element = self.get_element()
        # 这种方式经常点击不成功，感觉是页面刷新有影响
        # element.click()
        x, y = self._adapt_center(element)
        # if config.get_app('double_check'):
        #     logger.info('检查点击结果.')
        #     info_before = element.info
        #     self._driver.d.click(x, y)
        #     # 判断点击前后元素信息是否相同，如果相同就再点击一次
        #     if element.exists:
        #         if element.info == info_before:
        #             logger.debug('点击失败，再点一次')
        #             self.error_handler()
        #             self._driver.d.click(x, y)
        # else:
        #     self._driver.d.click(x, y)
        self._driver.d.click(x, y)

    def click_exists(self, timeout=3):
        logger.info(f"click if exists")
        if self.exists(timeout=timeout):
            self.click()

    def set_text(self, text):
        logger.info(f"input: {text}")
        self.get_element().set_text(text)

    def set_password(self, text):
        logger.info(f'input password: {text}')
        self.get_element().click()
        self._driver.d(focused=True).set_text(text)

    def clear_text(self):
        logger.info("clear text")
        self.get_element().clear_text()

    def drag_to(self, *args, **kwargs):
        logger.info(f"drag to")
        self.get_element().drag_to(*args, **kwargs)

    def swipe_left(self):
        logger.info(f"swipe left")
        self.get_element().swipe("left")

    def swipe_right(self):
        logger.info(f"swipe right")
        self.get_element().swipe("right")

    def swipe_up(self):
        logger.info(f"swipe up")
        self.get_element().swipe("up")

    def swipe_down(self):
        logger.info(f"swipe down")
        self.get_element().swipe("down")


if __name__ == '__main__':
    pass


