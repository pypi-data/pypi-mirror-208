import time
from typing import Union
from urllib import parse

from kuto.core.android.driver import AndroidDriver
from kuto.core.api.request import HttpReq
from kuto.core.ios.driver import IosDriver
from kuto.core.web.selenium_driver import SeleniumDriver
from kuto.utils.config import config
from kuto.utils.log import logger
from kuto.running.config import KutoConfig
from kuto.utils.exceptions import (
    HostIsNull
)


class Page(object):
    """页面基类，用于pom模式封装"""

    def __init__(self, driver: Union[AndroidDriver, IosDriver, SeleniumDriver]):
        self.driver = driver

    @staticmethod
    def sleep(n):
        """休眠"""
        logger.info(f"休眠 {n} 秒")
        time.sleep(n)


class TestCase(HttpReq):
    """
    测试用例基类，所有测试用例需要继承该类
    """

    driver: Union[AndroidDriver, IosDriver, SeleniumDriver] = None

    # ---------------------初始化-------------------------------
    def start_class(self):
        """
        Hook method for setup_class fixture
        :return:
        """
        pass

    def end_class(self):
        """
        Hook method for teardown_class fixture
        :return:
        """
        pass

    @classmethod
    def setup_class(cls):
        cls.browser = KutoConfig.browser
        if cls.browser:
            cls.driver = SeleniumDriver(cls.browser)
        else:
            cls.driver = KutoConfig.driver
        cls().start_class()

    @classmethod
    def teardown_class(cls):
        if isinstance(cls().driver, SeleniumDriver):
            cls().driver.quit()
        cls().end_class()

    def start(self):
        """
        Hook method for setup_method fixture
        :return:
        """
        pass

    def end(self):
        """
        Hook method for teardown_method fixture
        :return:
        """
        pass

    def setup_method(self):
        self.start_time = time.time()
        if isinstance(self.driver, (AndroidDriver, IosDriver)):
            self.driver.start_app()
        self.start()

    def teardown_method(self):
        self.end()
        if self.driver is not None:
            self.driver.screenshot('case_end')
        if isinstance(self.driver, (AndroidDriver, IosDriver)):
            self.driver.stop_app()
        take_time = time.time() - self.start_time
        logger.debug("[run_time]: {:.2f} s".format(take_time))

    # 公共方法
    @staticmethod
    def sleep(n: float):
        """休眠"""
        logger.debug(f"等待: {n}s")
        time.sleep(n)

    # UI自动化
    def open(self, url=None):
        # 拼接域名
        if url is None:
            base_url = config.get_host()
            if not base_url:
                raise HostIsNull('请设置base_url')
            url = base_url
        else:
            if "http" not in url:
                base_url = config.get_host()
                if not base_url:
                    raise HostIsNull('请设置base_url')
                url = parse.urljoin(base_url, url)
        # 访问页面
        self.driver.open_url(url)
        # 添加请求头并刷新页面
        headers = config.get_login()
        self.driver.add_cookies_and_refresh(headers)

    def assert_in_page(self, expect_value, timeout=5):
        """断言页面包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.page_content
                logger.info(f"断言: 页面内容 包含 {expect_value}")
                assert expect_value in page_source, f"页面内容不包含 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.page_content
            logger.info(f"断言: 页面内容 包含 {expect_value}")
            assert expect_value in page_source, f"页面内容不包含 {expect_value}"

    def is_in_page(self, expect_value, timeout=5):
        """页面是否包含文本"""
        self.sleep(timeout)
        page_source = self.driver.page_content
        return True if expect_value in page_source else False

    def assert_not_in_page(self, expect_value, timeout=5):
        """断言页面不包含文本"""
        for _ in range(timeout + 1):
            try:
                page_source = self.driver.page_content
                logger.info(f"断言: 页面内容 不包含 {expect_value}")
                assert expect_value not in page_source, f"页面内容不包含 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            page_source = self.driver.page_content
            logger.info(f"断言: 页面内容 不包含 {expect_value}")
            assert expect_value not in page_source, f"页面内容仍然包含 {expect_value}"

    def is_title(self, expect_value=None, timeout=5):
        """断言页面标题等于"""
        for _ in range(timeout + 1):
            title = self.driver.title
            if expect_value == title:
                return True
            self.sleep(1)
        else:
            return False

    def assert_title(self, expect_value=None, timeout=5):
        """断言页面标题等于"""
        for _ in range(timeout + 1):
            try:
                title = self.driver.title
                logger.info(f"断言: 页面标题 {title} 等于 {expect_value}")
                assert expect_value == title, f"页面标题 {title} 不等于 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            title = self.driver.title
            logger.info(f"断言: 页面标题 {title} 等于 {expect_value}")
            assert expect_value == title, f"页面标题 {title} 不等于 {expect_value}"

    def is_in_title(self, expect_value=None, timeout=5):
        """断言页面标题等于"""
        for _ in range(timeout + 1):
            title = self.driver.title
            if expect_value in title:
                return True
            self.sleep(1)
        else:
            return False

    def assert_in_title(self, expect_value=None, timeout=5):
        """断言页面标题包含"""
        for _ in range(timeout + 1):
            try:
                title = self.driver.title
                logger.info(f"断言: 页面标题 {title} 包含 {expect_value}")
                assert expect_value in title, f"页面标题 {title} 不包含 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            title = self.driver.title
            logger.info(f"断言: 页面标题 {title} 包含 {expect_value}")
            assert expect_value in title, f"页面标题 {title} 不包含 {expect_value}"

    def assert_url(self, expect_value=None, timeout=5):
        """断言页面url等于"""
        for _ in range(timeout + 1):
            try:
                url = self.driver.url
                logger.info(f"断言: 页面url {url} 等于 {expect_value}")
                assert expect_value == url, f"页面url {url} 不等于 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            url = self.driver.url
            logger.info(f"断言: 页面url {url} 等于 {expect_value}")
            assert expect_value == url, f"页面url {url} 不等于 {expect_value}"

    def assert_in_url(self, expect_value=None, timeout=5):
        """断言页面url包含"""
        for _ in range(timeout + 1):
            try:
                url = self.driver.url
                logger.info(f"断言: 页面url {url} 包含 {expect_value}")
                assert expect_value in url, f"页面url {url} 不包含 {expect_value}"
                break
            except AssertionError:
                time.sleep(1)
        else:
            url = self.driver.url
            logger.info(f"断言: 页面url {url} 包含 {expect_value}")
            assert expect_value in url, f"页面url {url} 不包含 {expect_value}"

    def assert_alert_text(self, expect_value):
        """断言弹窗文本"""
        alert_text = self.driver.alert_text
        logger.info(f"断言: 弹窗文本 {alert_text} 等于 {expect_value}")
        assert expect_value == alert_text, f"弹窗文本 {alert_text} 等于 {expect_value}"

