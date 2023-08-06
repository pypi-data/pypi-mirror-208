import kuto


if __name__ == '__main__':
    # 主程序入口

    # 执行接口用例
    # kuto.main(
    #     host='https://app-pre.qizhidao.com',
    #     path='tests/test_api.py'
    # )

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
    kuto.main(
        platform='web',
        host='https://www.qizhidao.com/',
        path='tests/web',
        xdist=False
    )
