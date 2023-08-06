import kuto
from kuto import IosElem


class IndexPage(kuto.Page):
    ad = IosElem(text='close white big')
    my = IosElem(text='我的')
    setting = IosElem(text='settings navi')
    title = IosElem(text='设置')


class TestSearch(kuto.TestCase):
    def start(self):
        self.index_page = IndexPage(self.driver)

    def test_go_setting(self):
        self.index_page.ad.click_exists(timeout=5)
        self.index_page.my.click()
        self.index_page.setting.click()
        assert self.index_page.title.exists(timeout=3)


if __name__ == '__main__':
    kuto.main(
        platform='ios',
        deviceId='00008101-000E646A3C29003A',
        pkgName='com.qizhidao.company'
    )

