import kuto
from kuto import WebElem


class PatentPage(kuto.Page):
    """查专利首页"""
    search_input = WebElem(id_='driver-home-step1', desc='查专利首页输入框')
    search_submit = WebElem(id_='driver-home-step2', desc='查专利首页搜索确认按钮')
    search_result_1 = WebElem(xpath='//*[@id="searchResultContentviewID"]/div[1]/div[1]', desc='第一条检索结果')
