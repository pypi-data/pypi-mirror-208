import kuto


class TestCaseClass(kuto.TestCase):

    def test_case1(self):
        payload = {"type": 2}
        self.post('/qzd-bff-app/qzd/v1/home/getToolCardListForPc', json=payload)
        self.assertEq('code', 0)


if __name__ == '__main__':
    kuto.main(
        host='https://app-pre.qizhidao.com',
        path='test_api.py::TestCaseClass::test_case1'
    )
