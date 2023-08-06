import kuto
from kuto import AdrElem


class HomePage(kuto.Page):
    """首页"""
    ad = AdrElem(resourceId='com.qizhidao.clientapp:id/bottom_btn')
    my = AdrElem(text='我的')
    setting = AdrElem(resourceId='com.qizhidao.clientapp:id/me_top_bar_setting_iv')


class TestSearch(kuto.TestCase):

    def start(self):
        self.page = HomePage(self.driver)

    def test_go_setting(self):
        self.page.ad.click_exists(timeout=5)
        self.page.my.click()
        self.page.setting.click()
        self.assert_in_page('设置')


if __name__ == '__main__':
    kuto.main(
        platform='android',
        deviceId='UJK0220521066836',
        pkgName='com.qizhidao.clientapp'
    )

