import kuto
from kuto import AdrElem


class HomePage(kuto.Page):
    """首页"""
    ad_close = AdrElem(res_id='com.qizhidao.clientapp:id/bottom_btn', desc='首页广告关闭按钮')
    my_entry = AdrElem(res_id='com.qizhidao.clientapp:id/bottom_view', index=2, desc='我的入口')
    setting_entry = AdrElem(res_id='com.qizhidao.clientapp:id/me_top_bar_setting_iv', desc='设置入口')
