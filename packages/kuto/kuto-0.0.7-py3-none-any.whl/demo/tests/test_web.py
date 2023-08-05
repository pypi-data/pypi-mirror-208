import kuto
from kuto import data, SeleElem


class PatentPage(kuto.Page):
    """查专利首页"""
    search_input = SeleElem(css='#driver-home-step1')
    search_submit = SeleElem(css='#driver-home-step2')
    search_result_1 = SeleElem(css='#searchResultContentviewID > '
                                   'div.card-view__wrapper > '
                                   'div:nth-child(1) > '
                                   'div.card-view-left__top > div:nth-child(2) > div > a > span')


class TestPatentSearch(kuto.TestCase):

    def start(self):
        self.page = PatentPage(self.driver)

    @data(["无人机"])
    def test_search(self, param):
        """搜索无人机"""
        self.open()
        self.page.search_input.set_text(param)
        self.page.search_submit.click()
        first_result = self.page.search_result_1.text
        assert param in first_result, f'{first_result} 不包含 {param}'
        self.driver.screenshot('search_result')


if __name__ == '__main__':
    kuto.main(
        platform='web',
        browserName='Chrome',
        host='https://patents.qizhidao.com/'
    )
