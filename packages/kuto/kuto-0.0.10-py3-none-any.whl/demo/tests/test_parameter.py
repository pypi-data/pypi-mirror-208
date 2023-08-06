import kuto
from kuto import *


LIST_DATA = [
    {"name": "李雷", "age": "33"},
    {"name": "韩梅梅", "age": "30"}
]


class TestParameter(kuto.TestCase):
    """
    原则是无论是哪种方式，返回的数据必须是list，用例都通过"params"进行调用
    """

    @data(LIST_DATA)
    def test_list(self, params):
        print(params)

    @file_data(file='data.json')
    def test_json(self, params):
        print(params)

    @file_data(file='data.yml', key='names')
    def test_yaml(self, params):
        print(params)

    @file_data(file='data.csv')
    def test_csv(self, params):
        print(params)

    @file_data(file='data.xlsx', row=1)
    def test_excel(self, params):
        print(params)


if __name__ == '__main__':
    kuto.main(
        path='test_para.py::TestParameter::test_json'
    )
