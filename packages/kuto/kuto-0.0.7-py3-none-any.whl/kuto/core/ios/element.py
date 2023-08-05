import inspect
import time

from kuto.utils.exceptions import ElementNameEmptyException, NoSuchElementException, DriverNotFound
from kuto.utils.log import logger
from kuto.utils.config import config
from kuto.core.ios.driver import IosDriver


class IosElem(object):
    """
    IOS原生元素定义
    """

    def __init__(self,
                 driver: IosDriver = None,
                 name: str = None,
                 label: str = None,
                 value: str = None,
                 text: str = None,
                 className: str = None,
                 xpath: str = None,
                 index: int = 0):
        """
        @param driver,
        @param name,
        param label,
        param value,
        param text,
        param className,
        param xpath,
        param index: 索引
        """
        # if driver is None:
        #     raise DriverNotFound('该控件未传入IOS driver参数')
        # else:
        #     self._driver = driver
        self._driver = driver

        self._kwargs = {}
        if name is not None:
            self._kwargs["name"] = name
        if label is not None:
            self._kwargs["label"] = label
        if value is not None:
            self._kwargs["value"] = value
        if text is not None:
            self._kwargs["text"] = text
        if className is not None:
            self._kwargs["className"] = className

        self._xpath = xpath
        self._index = index

    def __get__(self, instance, owner):
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    def error_handler(self):
        """异常处理，暂时只支持text"""
        errors = config.get_app('errors')
        if errors:
            logger.info(f'处理异常弹窗: {errors}')
            for error in errors:
                self._driver.d(**error).click_exists()

    def _find_element(self, retry=3, timeout=3):
        """
        循环查找元素，查找失败先处理弹窗后重试
        @param retry: 重试次数
        @param timeout: 单次查找超时时间
        @return:
        """
        if self._xpath is not None:
            logger.info(f'查找元素: xpath={self._xpath}')
        else:
            logger.info(f'查找元素: {self._kwargs}[{self._index}]')

        self._element = self._driver.d.xpath(self._xpath) if \
            self._xpath else self._driver.d(**self._kwargs)[self._index]

        # 第一次查找
        try:
            if self._element.wait(timeout=timeout):
                return self._element
        except ConnectionError:
            logger.info('出现链接异常，重新连接IOS设备')
            # 由于WDA会意外链接错误
            self.driver = IosDriver(self.driver.device_id)
            time.sleep(5)

        # 失败重试
        if retry > 0:
            for i in range(retry):
                self.error_handler()
                logger.info(f'第{i + 1}次重试:')
                try:
                    if self._element.wait(timeout=timeout):
                        return self._element
                except ConnectionError:
                    logger.info('出现链接异常，重新连接IOS设备')
                    # 由于WDA会意外链接错误
                    self.driver = IosDriver(self.driver.device_id)
                    time.sleep(5)

        # 查找失败提示
        frame = inspect.currentframe().f_back
        caller = inspect.getframeinfo(frame)
        logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
        return None

    def get_element(self, retry=3, timeout=3):
        """
        针对元素定位失败的情况，抛出NoSuchElementException异常
        @param retry:
        @param timeout:
        @return:
        """
        element = self._find_element(retry=retry, timeout=timeout)
        if element is None:
            raise NoSuchElementException(f"[控件 {self._kwargs} 定位失败]")
        self._driver.screenshot("loc")
        return element

    @property
    def info(self):
        """获取元素信息"""
        logger.info(f"获取元素属性")
        return self.get_element(retry=0, timeout=1).info

    @property
    def text(self):
        """获取元素文本"""
        logger.info(f"获取元素text属性")
        return self.get_element().text

    @property
    def bounds(self):
        """获取元素bounds属性"""
        logger.info(f"获取元素的bounds属性")
        return self.get_element().bounds

    @property
    def rect(self):
        """获取元素左上角坐标和宽高"""
        logger.info(f"获取元素的左上角坐标和宽高")
        return [item * self._driver.d.scale for item in list(self.get_element().bounds)]

    def exists(self, timeout=3):
        """
        判断元素是否存在当前页面
        @param timeout:
        @return:
        """
        logger.info(f"判断元素是否存在:")
        element = self._find_element(retry=0, timeout=timeout)
        if element is None:
            return False
        return True

    def click(self, retry=3, timeout=3):
        """
        单击
        @param: retry，重试次数
        @param: timeout，每次重试超时时间
        """
        element = self.get_element(retry=retry, timeout=timeout)
        logger.info('开始点击')
        # if config.get_app('double_check'):
        #     logger.info('点击结果检查.')
        #     info_before = element.info
        #     element.click()
        #     time.sleep(1)
        #     # # 判断点击前后元素信息是否相同，如果相同就再点击一次
        #     if element.exists:
        #         if element.info == info_before:
        #             logger.debug('点击失败，再点一次')
        #             self.error_handler()
        #             element.click()
        # else:
        #     element.click()
        element.click()
        logger.info('点击成功')

    def click_exists(self, timeout=3):
        """元素存在时点击"""
        logger.info(f"存在才点击元素")
        if self.exists(timeout=timeout):
            self.click()

    def clear_text(self):
        """清除文本"""
        logger.info("清除文本")
        self.get_element().clear_text()

    def set_text(self, text):
        """输入内容"""
        logger.info(f"输入框文本 {text}")
        self.get_element().set_text(text)

    def scroll(self, direction=None):
        """
        滑动到元素可见的位置
        @param: direction，方向，"up", "down", "left", "right"
        @return:
        """
        if direction is not None:
            self.get_element().scroll(direction=direction)
        else:
            self.get_element().scroll()

    def swipe_left(self):
        """往左滑动"""
        self.get_element().swipe("left")

    def swipe_right(self):
        """往右滑动"""
        self.get_element().swipe("right")

    def swipe_up(self):
        """往上滑动"""
        self.get_element().swipe("up")

    def swipe_down(self):
        """往下滑动"""
        self.get_element().swipe("down")


if __name__ == '__main__':
    pass




