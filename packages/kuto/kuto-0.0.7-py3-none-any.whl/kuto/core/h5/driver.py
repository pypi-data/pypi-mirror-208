import os
import subprocess
import sys
import time

# import allure
import allure
import requests
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException

from kuto.core.android.driver import AndroidDriver
from kuto.utils.exceptions import ScreenFailException
from kuto.utils.log import logger
from kuto.utils.webdriver_manager_extend import ChromeDriverManager


class ChromeConfig:
    headless = False
    options = None
    command_executor = ""


def get_server_chrome_versions():
    """获取淘宝镜像网站上所有的版本列表"""
    version_list = []
    url = "https://registry.npmmirror.com/-/binary/chromedriver/"
    rep = requests.get(url).json()
    for item in rep:
        version_list.append(item["name"])
    return version_list


def get_webview_version(serial_no, pkg_name):
    """通过shell命令获取webview对应chrome的版本号"""
    # 获取应用的pid
    pid = subprocess.getoutput(f"adb -s {serial_no} shell ps | grep {pkg_name}").split(
        " "
    )[6]
    print(pid)

    # 获取webview的socket名称
    socket_name = subprocess.getoutput(
        f"adb -s {serial_no} shell cat /proc/net/unix | grep --binary-file=text webview"
    ).split(" ")[-1][1:]
    print(socket_name)

    # 将webview端口转发到本地
    cmd = f"adb -s {serial_no} forward tcp:5000 localabstract:{socket_name}"
    print(cmd)
    subprocess.getoutput(cmd)

    # 请求本地服务，获取版本号
    version_data = requests.get("http://127.0.0.1:5000/json/version").json()
    print(version_data)
    version = version_data["Browser"].split("/")[1]
    print(version)

    return version


def get_driver_version(serial_no, pkg_name):
    """获取应用对应的淘宝镜像的chromedriver的版本号"""
    webview_version = get_webview_version(serial_no, pkg_name)

    version_list = get_server_chrome_versions()
    if webview_version in version_list:
        return webview_version
    else:
        for version in version_list:
            if version[0:10] == webview_version[0:10]:
                return version.split("/")[0]
        else:
            print("淘宝镜像未找到匹配本机的chromedriver版本")
            sys.exit()


class H5Driver(object):

    def __init__(self, android_driver: AndroidDriver, timeout=60):
        serial_no = android_driver.device_id
        pkg_name = android_driver.pkg_name

        logger.info(f"启动H5Driver for {serial_no}")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("androidDeviceSerial", serial_no)
        options.add_experimental_option("androidPackage", pkg_name)
        options.add_experimental_option("androidUseRunningApp", True)
        options.add_experimental_option("androidProcess", pkg_name)
        for i in range(3):
            logger.debug(f"第 {i + 1} 次在淘宝镜像查找驱动:")
            try:
                version = get_driver_version(serial_no, pkg_name)
                self.d = webdriver.Chrome(
                    executable_path=ChromeDriverManager(version=version).install(),
                    options=options,
                )
                logger.debug("h5Driver初始化成功")
                break
            except Exception as e:
                logger.debug(f"第 {i + 1} 次查找失败: {str(e)}")
                logger.debug(f"第 {i + 1} 次重试")
                time.sleep(3)
        else:
            logger.debug("重试3次失败，h5Driver初始化失败")
            sys.exit()

        # 设置页面加载超时时间
        self.d.set_page_load_timeout(timeout)

    @property
    def page_content(self):
        page_source = self.d.page_source
        logger.info(f"获取页面内容: \n{page_source}")
        return page_source

    @property
    def title(self):
        logger.info("获取页面标题")
        title = self.d.title
        logger.info(title)
        return title

    @property
    def url(self):
        logger.info("获取页面url")
        url = self.d.current_url
        logger.info(url)
        return url

    @property
    def alert_text(self):
        logger.info("获取alert的文本")
        try:
            alert_text = self.d.switch_to.alert.text
        except NoAlertPresentException:
            logger.info(f'没有出现alert')
            return None
        return alert_text

    def open_url(self, url):
        logger.info(f"访问: {url}")
        self.d.get(url)

    def back(self):
        logger.info("返回上一页")
        self.d.back()

    def screenshot(self, file_name='截图', with_time=True):
        """
        截图并保存到预定路径
        @param with_time: 是否带时间戳
        @param file_name: foo.png or fool
        @return:
        """
        try:
            # 把文件名处理成test.png的样式
            if "." in file_name:
                file_name = file_name.split(r".")[0]
            # 截图并保存到当前目录的images文件夹中
            local_path = os.getcwd()
            relative_path = os.path.join("reports", "screenshot")
            dir_path = os.path.join(local_path, relative_path)
            if os.path.exists(dir_path) is False:
                os.mkdir(dir_path)
            if with_time:
                time_str = time.strftime("%Y-%m-%d_%H_%M_%S")
                file_name = f"{time_str}_{file_name}.png"
            else:
                file_name = f'{file_name}.png'

            file_path = os.path.join(dir_path, file_name)
            logger.info(f"截图保存至: {os.path.join(relative_path, file_name)}")
            self.d.save_screenshot(file_path)
            # 上传allure报告
            allure.attach.file(
                file_path,
                attachment_type=allure.attachment_type.PNG,
                name=f"{file_name}",
            )
            return file_path
        except Exception as e:
            raise ScreenFailException(f"{file_name} 截图失败\n{str(e)}")

    def get_windows(self):
        logger.info(f"获取当前打开的窗口列表")
        return self.d.window_handles

    def switch_window(self, old_windows):
        logger.info("切换到最新的window")
        current_windows = self.d.window_handles
        newest_window = [
            window for window in current_windows if window not in old_windows
        ][0]
        self.d.switch_to.window(newest_window)

    def switch_to_frame(self, frame_id):
        logger.info(f"切换到frame {frame_id}")
        self.d.switch_to.frame(frame_id)

    def switch_to_frame_out(self):
        logger.info("从frame中切出来")
        self.d.switch_to.default_content()

    def execute_js(self, script, *args):
        logger.info(f"执行js脚本: \n{script}")
        self.d.execute_script(script, *args)

    def click_elem(self, element):
        logger.info(f"点击元素: {element}")
        self.d.execute_script("arguments[0].click();", element)

    def accept_alert(self):
        logger.info("同意确认框")
        self.d.switch_to.alert.accept()

    def dismiss_alert(self):
        logger.info("取消确认框")
        self.d.switch_to.alert.dismiss()
