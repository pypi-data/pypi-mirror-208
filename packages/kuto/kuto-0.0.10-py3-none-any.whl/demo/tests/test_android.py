import kuto

from page.adr_page import HomePage


class TestSearch(kuto.TestCase):

    def start(self):
        self.page = HomePage(self.driver)

    def test_go_setting(self):
        self.page.my_entry.click()
        self.page.setting_entry.click()
        self.assert_in_page('设置')


if __name__ == '__main__':
    # 连接本地设备
    kuto.main(
        platform='android',
        device_id='UJK0220521066836',
        pkg_name='com.qizhidao.clientapp'
    )

