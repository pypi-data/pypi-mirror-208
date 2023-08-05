import os.path
import sys

run_content = """
import kuto


if __name__ == '__main__':
    # 主程序入口

    # 执行接口用例
    kuto.main(
        host='https://app-pre.qizhidao.com',
        path='tests/test_api.py'
    )

    # 执行安卓用例
    # kuto.main(
    #     platform='android',
    #     device_id='UJK0220521066836',
    #     pkg_name='com.qizhidao.clientapp',
    #     path='tests/test_adr.py'
    # )

    # 执行ocr用例
    # kuto.main(
    #     platform='android',
    #     device_id='UJK0220521066836',
    #     pkg_name='com.qizhidao.clientapp',
    #     path='tests/test_ocr.py'
    # )

    # 执行图像识别用例
    # kuto.main(
    #     platform='ios',
    #     device_id='00008101-000E646A3C29003A',
    #     pkg_name='com.qizhidao.company',
    #     path='tests/test_image.py'
    # )

    # 执行ios用例
    # kuto.main(
    #     platform='ios',
    #     device_id='00008101-000E646A3C29003A',
    #     pkg_name='com.qizhidao.company',
    #     path='tests/test_ios.py'
    # )

    # 执行web用例
    # kuto.main(
    #     platform='web',
    #     host='https://patents.qizhidao.com/',
    #     path='tests/test_web.py'
    # )

"""

page_content_android = """import kuto
from kuto import AdrElem


class HomePage(kuto.Page):
    ad_close = AdrElem(res_id='com.qizhidao.clientapp:id/bottom_btn', desc='首页广告关闭按钮')
    my_entry = AdrElem(res_id='com.qizhidao.clientapp:id/bottom_view', index=2, desc='我的入口')
    setting_entry = AdrElem(res_id='com.qizhidao.clientapp:id/me_top_bar_setting_iv', desc='设置入口')

"""

case_content_android = """import kuto

from page.adr_page import HomePage


class TestSearch(kuto.TestCase):

    def start(self):
        self.page = HomePage(self.driver)

    def test_pom(self):
        self.page.my_entry.click()
        self.page.setting_entry.click()
        self.assert_in_page('设置')

"""

case_content_ios = """import kuto


class TestSearch(kuto.TestCase):

    def test_normal(self):
        self.elem(text='我的', desc='我的入口').click()
        self.elem(text='settings navi', desc='设置入口').click()
        self.assert_in_page('设置')

"""

page_content_web = """import kuto
from kuto import WebElem


class PatentPage(kuto.Page):
    search_input = WebElem(id_='driver-home-step1', desc='查专利首页输入框')
    search_submit = WebElem(id_='driver-home-step2', desc='查专利首页搜索确认按钮')

"""

case_content_web = """import kuto

from page.web_page import PatentPage


class TestPatentSearch(kuto.TestCase):

    def start(self):
        self.page = PatentPage(self.driver)

    def test_pom(self):
        self.open()
        self.page.search_input.set_text('无人机')
        self.page.search_submit.click()
        self.assert_in_page('无人机')

"""

case_content_api = """import kuto


class TestGetToolCardListForPc(kuto.TestCase):

    def test_getToolCardListForPc(self):
        payload = {"type": 2}
        headers = {"user-agent-web": "X/b67aaff2200d4fc2a2e5a079abe78cc6"}
        self.post('/qzd-bff-app/qzd/v1/home/getToolCardListForPc', headers=headers, json=payload)
        self.assert_eq('code', 0)

"""


def create_scaffold(platform):
    """create scaffold with specified project name."""

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    # 新增测试数据目录
    create_folder(os.path.join("tests"))
    if platform in ["android", "ios", "web"]:
        create_folder(os.path.join("page"))
    create_folder(os.path.join("reports"))
    if platform in ["android", "ios", "web"]:
        create_folder(os.path.join("reports", "screenshot"))
    create_folder(os.path.join("data"))
    # 新增安卓测试用例
    create_file(
        "run.py",
        run_content,
    )
    if platform == "android":
        # 新增安卓测试用例
        create_file(
            os.path.join("tests", "test_adr.py"),
            case_content_android,
        )
        create_file(
            os.path.join("page", "adr_page.py"),
            page_content_android,
        )

    elif platform == "ios":
        # 新增ios测试用例
        create_file(
            os.path.join("tests", "test_ios.py"),
            case_content_ios,
        )
    elif platform == "web":
        # 新增web测试用例
        create_file(
            os.path.join("tests", "test_web.py"),
            case_content_web,
        )
        create_file(
            os.path.join("page", "web_page.py"),
            page_content_web,
        )
    elif platform == "api":
        # 新增接口测试用例
        create_file(
            os.path.join("tests", "test_api.py"),
            case_content_api,
        )
    else:
        print("请输入正确的平台: android、ios、web、api")
        sys.exit()
