import os
import shutil
import subprocess
import time

# import allure
import allure
import wda

from kuto.core.ios.common import get_tcp_port, check_device
from kuto.utils.exceptions import ScreenFailException, PkgIsNull, DeviceNotFoundException
from kuto.utils.log import logger
from kuto.core.ios.common import TideviceUtil
from kuto.testdata import get_int


def _start_wda_xctest(udid: str, port, wda_bundle_id=None) -> bool:
    xctool_path = shutil.which("tidevice")
    logger.info(f"WDA is not running, exec: {xctool_path} -u {udid} wdaproxy --port {port} -B {wda_bundle_id}")
    args = []
    if udid:
        args.extend(["-u", udid])
    args.append("wdaproxy")
    args.extend(["--port", str(port)])
    if wda_bundle_id is not None:
        args.extend(["-B", wda_bundle_id])
    p = subprocess.Popen([xctool_path] + args)
    time.sleep(3)
    if p.poll() is not None:
        logger.warning("xctest launch failed")
        return False
    return True


class IosDriver(object):

    def __init__(self, device_id=None, pkg_name=None):
        logger.info(f'init ios driver.')

        self.pkg_name = pkg_name
        if not self.pkg_name:
            raise PkgIsNull('应用bundle_id不能为空')
        self.device_id = device_id
        if not self.device_id:
            raise DeviceNotFoundException('udid不能为空')

        self.device_id = check_device(self.device_id)  # 检查本地设备是否已连接
        self.port = get_tcp_port(self.device_id)
        self.wda_url = f"http://localhost:{self.port}"
        self.d = wda.Client(self.wda_url)

        # check if wda is ready
        if self.d.is_ready():
            logger.info('wda is ready.')
        else:
            logger.info('wda is not ready, start now.')
            _start_wda_xctest(self.device_id, port=self.port)


    @property
    def device_info(self):
        """设备信息"""
        info = self.d.device_info()
        logger.info(f"设备信息: {info}")
        return info

    @property
    def page_content(self):
        """获取页面xml内容"""
        logger.info('获取页面xml')
        page_source = self.d.source(accessible=False)
        return page_source

    def install_app(self, ipa_url, new=True, pkg_name=None):
        """安装应用
        @param ipa_url: ipa链接
        @param new: 是否先卸载
        @param pkg_name: 应用包名
        @return:
        """
        if new is True:
            pkg_name = pkg_name if pkg_name else self.pkg_name
            self.uninstall_app(pkg_name)

        TideviceUtil.install_app(self.device_id, ipa_url)

    def uninstall_app(self, pkg_name=None):
        """卸载应用"""
        pkg_name = pkg_name if pkg_name else self.pkg_name

        TideviceUtil.uninstall_app(self.device_id, pkg_name)

    def start_app(self, pkg_name=None, stop=True):
        """启动应用
        @param pkg_name: 应用包名
        @param stop: 是否先停止应用
        """
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f"启动应用: {pkg_name}")
        if stop is True:
            self.d.app_terminate(pkg_name)
        self.d.app_start(pkg_name)

    def stop_app(self, pkg_name=None):
        """停止应用"""
        if not pkg_name:
            pkg_name = self.pkg_name
        logger.info(f"停止应用: {pkg_name}")
        self.d.app_terminate(pkg_name)

    def back(self):
        """返回上一页"""
        logger.info("返回上一页")
        time.sleep(1)
        self.d.swipe(0, 100, 100, 100)

    def set_text(self, value):
        """输入内容"""
        logger.info(f"输入: {value}")
        self.d.send_keys(value)

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
                time_str = time.strftime(f"%Y-%m-%d_%H_%M_%S_{get_int(min_size=1, max_size=1000)}")
                file_name = f"{time_str}_{file_name}.png"
            else:
                file_name = f'{file_name}.png'

            file_path = os.path.join(dir_path, file_name)
            logger.info(f"截图保存至: {os.path.join(relative_path, file_name)}")
            self.d.screenshot(file_path)
            # 上传allure报告
            allure.attach.file(
                file_path,
                attachment_type=allure.attachment_type.PNG,
                name=f"{file_name}",
            )
            return file_path
        except Exception as e:
            raise ScreenFailException(f"{file_name} 截图失败\n{str(e)}")

    def click(self, x, y):
        """点击坐标"""
        logger.info(f"点击坐标: ({x}, {y})")
        logger.info(f"{self.device_id} Tap point ({x}, {y})")
        self.d.appium_settings({"snapshotMaxDepth": 0})
        self.d.tap(x, y)
        self.d.appium_settings({"snapshotMaxDepth": 50})
        time.sleep(1)

    def click_alerts(self, alert_list: list):
        """点击弹窗"""
        try:
            self.d.alert.click(alert_list)
        except:
            pass

    def swipe(self, start_x, start_y, end_x, end_y, duration=0):
        """根据坐标滑动"""
        logger.info(f"从坐标({start_x}, {start_y})滑动到({end_x}, {end_y})")
        logger.info(
            f"{self.device_id} swipe from point ({start_x}, {start_y}) to ({end_x}, {end_y})"
        )
        self.d.appium_settings({"snapshotMaxDepth": 2})
        self.d.swipe(int(start_x), int(start_y), int(end_x), int(end_y), duration)
        self.d.appium_settings({"snapshotMaxDepth": 50})
        time.sleep(2)

    def swipe_left(self, start_percent=1, end_percent=0.5):
        """往左滑动"""
        logger.info("往左边滑动")
        w, h = self.d.window_size()
        self.swipe(start_percent * (w - 1), h / 2, end_percent * w, h / 2)

    def swipe_right(self, start_percent=0.5, end_percent=1):
        """往右滑动"""
        logger.info("往右边滑动")
        w, h = self.d.window_size()
        self.swipe(start_percent * w, h / 2, end_percent * (w - 1), h / 2)

    def swipe_up(self, start_percent=0.8, end_percent=0.2):
        """往上滑动"""
        logger.info("往上边滑动")
        w, h = self.d.window_size()
        self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)

    def swipe_down(self, start_percent=0.2, end_percent=0.8):
        """往下滑动"""
        logger.info("往下面滑动")
        w, h = self.d.window_size()
        self.swipe(w / 2, start_percent * h, w / 2, end_percent * h)

    def health_check(self):
        """检查设备连接状态"""
        logger.info("健康检查")
        self.d.healthcheck()

    def open_url(self, url):
        """
        打开schema
        @param: url，schema链接，taobao://m.taobao.com/index.htm
        @return:
        """
        logger.info(f"打开url: {url}")
        self.d.open_url(url)


if __name__ == '__main__':
    driver = IosDriver('00008101-000E646A3C29003A', 'com.qizhidao.company')
    driver.install_app('http://172.16.5.225:8081/AppUpdateTest/pre_qizhiyun_client_4.3.2.ipa')



