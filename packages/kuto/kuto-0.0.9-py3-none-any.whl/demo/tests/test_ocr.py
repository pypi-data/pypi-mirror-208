import kuto
from kuto import *
from kuto.core.ocr.element import OCRElem


class HomePage(kuto.Page):
    """APP首页"""
    ad_close = AdrElem(res_id='com.qizhidao.clientapp:id/bottom_btn', desc='广告关闭按钮')


class PatentPage(kuto.Page):
    """查专利首页"""
    patent_entry = OCRElem(text='查专利', desc='查专利入口')
    report_entry = OCRElem(text='分析报告', desc='分析报告入口')


class TestAdvancedSearch(kuto.TestCase):

    def start(self):
        self.hp = HomePage(self.driver)
        self.pp = PatentPage(self.driver)

    def test_go_report(self):
        self.hp.ad_close.click_exists()
        self.pp.patent_entry.click()
        self.pp.report_entry.click()
        self.sleep(10)


if __name__ == '__main__':
    kuto.main(
        platform='android',
        device_id='UJK0220521066836',
        pkg_name='com.qizhidao.clientapp'
    )

