"""
@Author: kang.yang
@Date: 2023/5/9 10:02
"""
import allure


def upload_pic(file_path: str):
    """上传图片到allure报告"""
    print("上传图片到allure报告")
    file_name = "截图"
    print(file_name)
    allure.attach.file(
        file_path,
        attachment_type=allure.attachment_type.PNG,
        name={file_name}
    )
