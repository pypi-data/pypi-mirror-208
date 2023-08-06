import os
import subprocess

from kuto.utils.log import logger
from kuto.utils.exceptions import DeviceNotFoundException


def get_device_list():
    """获取当前连接的设备列表"""
    cmd = 'tidevice list'
    output = os.popen(cmd).read()
    device_list = [item.split(' ')[0] for item in output.split('\n') if item]
    if len(device_list) > 0:
        return device_list
    else:
        raise DeviceNotFoundException(msg=f"无已连接设备")


def get_current_device():
    """连接一个手机时，返回设备id"""
    device_list = get_device_list()
    return device_list[0]


def get_tcp_port(udid: str):
    """获取可用端口号"""
    port = int(udid.split('-')[0])
    return port


def check_device(device_id):
    """检查设备是否已连接"""
    if device_id is None:
        device_id = get_current_device()
        return device_id
    else:
        if device_id in get_device_list():
            return device_id
        else:
            raise DeviceNotFoundException(msg=f"设备 {device_id} 未连接")


class TideviceUtil:
    """
    tidevice常用功能的封装
    """

    @staticmethod
    def uninstall_app(device_id=None, pkg_name=None):
        """卸载应用"""
        cmd = f"tidevice -u {device_id} uninstall {pkg_name}"
        logger.info(f"卸载应用: {pkg_name}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{device_id} 卸载应用{pkg_name} 成功")
            return
        else:
            logger.info(f"{device_id} 卸载应用{pkg_name}失败，因为{output}")

    @staticmethod
    def install_app(device_id=None, ipa_url=None):
        """安装应用
        """
        cmd = f"tidevice -u {device_id} install {ipa_url}"
        logger.info(f"安装应用: {ipa_url}")
        output = subprocess.getoutput(cmd)
        if "Complete" in output.split()[-1]:
            logger.info(f"{device_id} 安装应用{ipa_url} 成功")
            return
        else:
            logger.info(f"{device_id} 安装应用{ipa_url}失败，因为{output}")


if __name__ == '__main__':
    print(get_device_list())

