import kuto
from kuto import *
from kuto.core.image.element import ImageElem


class HomePage(kuto.Page):
    """APP首页"""
    ad_close = IosElem(label='close white big', desc='广告关闭按钮')
    patent_entry = IosElem(text='查专利', desc='查专利入口')


class PatentSearch(kuto.Page):
    """查专利"""
    report_entry = ImageElem(image='tpl1678093612402.png', desc='分析报告')


class TestSearch(kuto.TestCase):

    def start(self):
        self.hp = HomePage(self.driver)
        self.ps = PatentSearch(self.driver)

    def test_go_report(self):
        self.hp.ad_close.click_exists()
        self.hp.patent_entry.click()
        self.ps.report_entry.click()
        self.sleep(10)


if __name__ == '__main__':
    kuto.main(
        platform='ios',
        device_id='00008101-000E646A3C29003A',
        pkg_name='com.qizhidao.company'
    )
