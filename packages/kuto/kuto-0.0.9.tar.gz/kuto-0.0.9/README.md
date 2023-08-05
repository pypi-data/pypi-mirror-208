# 介绍

[Gitee](https://gitee.com/bluepang2021/kuto)

AppUI/WebUI/HTTP automation testing framework based on pytest.

> 基于pytest 的 App UI/Web UI/HTTP自动化测试框架。

## 特点

* 集成`facebook-wda`/`uiautomator2`/`selenium`/`requests`
* 支持安卓 UI/IOS UI/Web UI/HTTP接口测试
* 集成`allure`, 支持HTML格式的测试报告
* 提供脚手架，快速生成自动化测试项目
* 提供强大的`数据驱动`，支持json、yaml、csv、excel
* 提供丰富的断言
* 支持生成随机测试数据
* 支持设置用例依赖


## 三方依赖

* Allure：https://github.com/allure-framework/allure2
* WebDriverAgent：https://github.com/appium/WebDriverAgent

## Install

```shell
> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple kuto
```

## 🤖 Quick Start

1、查看帮助：
```shell
usage: kuto [-h] [-v] [-n PROJECT_NAME] [-p PLATFORM] [-i INSTALL]

全平台自动化测试框架

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         版本号
  -i INSTALL, --install INSTALL
                        浏览器驱动名称

```

2、运行项目：

* ✔️ 在`pyCharm`中右键执行(需要把项目的单元测试框架改成unittests)

* ✔️ 通过命令行工具执行。

3、查看报告

运行`allure server reports`浏览器会自动调起报告（需先安装配置allure）


## 🔬 Demo

[demo](/demo) 提供了丰富实例，帮你快速了解kuto的用法。

### 安卓APP 测试

* IOS、Web类似

```python
import kuto

from page.adr_page import HomePage


class TestCaseClass(kuto.TestCase):

    def start(self):
        self.page = HomePage(self.driver)

    def test_case1(self):
        self.page.my_entry.click()
        self.page.setting_entry.click()
        self.assert_in_page('设置')
```

__说明：__

* 创建测试类必须继承 `kuto.TestCase`。
* 测试用例文件命名必须以 `test` 开头。
* kuto的封装了`assert_in_page`、`assert_title` 等断言方法。
* 如果用例间有耦合关系，建议使用pom模式，方便复用；否则，使用普通模式即可
  - pom模式需要继承kuto.Page
  - 页面初始化的时候需要传入driver

### HTTP 测试

```python
import kuto


class TestCaseClass(kuto.TestCase):

    def test_case1(self):
        payload = {"type": 2}
        headers = {"user-agent-web": "X/b67aaff2200d4fc2a2e5a079abe78cc6"}
        self.post('/qzd-bff-app/qzd/v1/home/getToolCardListForPc', headers=headers, json=payload)
        self.assertEq('code', 0)
```

__说明：__

* 创建测试类必须继承 `kuto.TestCase`。
* 测试用例文件命名必须以 `test` 开头。
* kuto的封装了`assertEq`、`assertLenEq` 和 `assertLenGt`等断言方法。

### 参数化

```python
import kuto
from kuto import data, file_data


LIST_DATA = [
    {"name": "李雷", "age": "33"},
    {"name": "韩梅梅", "age": "30"}
]


class TestParameter(kuto.TestCase):
    """
    原则是无论是哪种方式，返回的数据必须是list，用例都通过"param"进行调用
    """

    @data(LIST_DATA)
    def test_list(self, param):
        print(param)

    @file_data(file='data.json')
    def test_json(self, param):
        print(param)

    @file_data(file='data.yml', key='names')
    def test_yaml(self, param):
        print(param)

    @file_data(file='data.csv')
    def test_csv(self, param):
        print(param)

    @file_data(file='data.xlsx', row=1)
    def test_excel(self, param):
        print(param)

```

### Run the test

```python
import kuto

kuto.main()  # 当前文件，pycharm中需要把默认的单元测试框架改成unittests
kuto.main(path="./")  # 当前目录
kuto.main(path="./test_dir/")  # 指定目录
kuto.main(path="./test_dir/test_api.py")  # 指定特定文件
kuto.main(path="./test_dir/test_api.py::TestCaseClass:test_case1") # 指定特定用例
```

### 感谢

感谢从以下项目中得到思路和帮助。

* [seldom](https://github.com/SeldomQA/seldom)

* [selenium](https://www.selenium.dev/)

* [uiautomator2](https://github.com/openatx/uiautomator2)
  
* [facebook-wda](https://github.com/openatx/facebook-wda)

* [requests](https://github.com/psf/requests)

## 高级用法

### 随机测试数据

测试数据是测试用例的重要部分，有时不能把测试数据写死在测试用例中，比如注册新用户，一旦执行过用例那么测试数据就已经存在了，所以每次执行注册新用户的数据不能是一样的，这就需要随机生成一些测试数据。

kuto 提供了随机获取测试数据的方法。

```python
import kuto
from kuto import testdata


class TestYou(kuto.TestCase):
    
    def test_case(self):
        """a simple test case """
        word = testdata.get_word()
        print(word)
        
if __name__ == '__main__':
    kuto.main()
```

通过`get_word()` 随机获取一个单词，然后对这个单词进行搜索。

**更多的方法**

```python
from kuto.testdata import *
# 随机一个名字
print("名字：", first_name())
print("名字(男)：", first_name(gender="male"))
print("名字(女)：", first_name(gender="female"))
print("名字(中文男)：", first_name(gender="male", language="zh"))
print("名字(中文女)：", first_name(gender="female", language="zh"))
# 随机一个姓
print("姓:", last_name())
print("姓(中文):", last_name(language="zh"))
# 随机一个姓名
print("姓名:", username())
print("姓名(中文):", username(language="zh"))
# 随机一个生日
print("生日:", get_birthday())
print("生日字符串:", get_birthday(as_str=True))
print("生日年龄范围:", get_birthday(start_age=20, stop_age=30))
# 日期
print("日期(当前):", get_date())
print("日期(昨天):", get_date(-1))
print("日期(明天):", get_date(1))
# 数字
print("数字(8位):", get_digits(8))
# 邮箱
print("邮箱:", get_email())
# 浮点数
print("浮点数:", get_float())
print("浮点数范围:", get_float(min_size=1.0, max_size=2.0))
# 随机时间
print("当前时间:", get_now_datetime())
print("当前时间(格式化字符串):", get_now_datetime(strftime=True))
print("未来时间:", get_future_datetime())
print("未来时间(格式化字符串):", get_future_datetime(strftime=True))
print("过去时间:", get_past_datetime())
print("过去时间(格式化字符串):", get_past_datetime(strftime=True))
# 随机数据
print("整型:", get_int())
print("整型32位:", get_int32())
print("整型64位:", get_int64())
print("MD5:", get_md5())
print("UUID:", get_uuid())
print("单词:", get_word())
print("单词组(3个):", get_words(3))
print("手机号:", get_phone())
print("手机号(移动):", get_phone(operator="mobile"))
print("手机号(联通):", get_phone(operator="unicom"))
print("手机号(电信):", get_phone(operator="telecom"))
```

* 运行结果

```shell
名字： Hayden
名字（男）： Brantley
名字（女）： Julia
名字（中文男）： 觅儿
名字（中文女）： 若星
姓: Lee
姓（中文）: 白
姓名: Genesis
姓名（中文）: 廉高义
生日: 2000-03-11
生日字符串: 1994-11-12
生日年龄范围: 1996-01-12
日期（当前）: 2022-09-17
日期（昨天）: 2022-09-16
日期（明天）: 2022-09-18
数字(8位): 48285099
邮箱: melanie@yahoo.com
浮点数: 1.5315717275531858e+308
浮点数范围: 1.6682402084146244
当前时间: 2022-09-17 23:33:22.736031
当前时间(格式化字符串): 2022-09-17 23:33:22
未来时间: 2054-05-02 11:33:47.736031
未来时间(格式化字符串): 2070-08-28 16:38:45
过去时间: 2004-09-03 12:56:23.737031
过去时间(格式化字符串): 2006-12-06 07:58:37
整型: 7831034423589443450
整型32位: 1119927937
整型64位: 3509365234787490389
MD5: d0f6c6abbfe1cfeea60ecfdd1ef2f4b9
UUID: 5fd50475-2723-4a36-a769-1d4c9784223a
单词: habitasse
单词组（3个）: уж pede. metus.
手机号: 13171039843
手机号(移动): 15165746029
手机号(联通): 16672812525
手机号(电信): 17345142737
```

### 用例的依赖

**depend**

`depend` 装饰器用来设置依赖的用例。

```python
import kuto
from kuto import depend


class TestDepend(kuto.TestCase):
    
    @depend(name='test_001')
    def test_001(self):
        print("test_001")
        
    @depend("test_001", name='test_002')
    def test_002(self):
        print("test_002")
        
    @depend(["test_001", "test_002"])
    def test_003(self):
        print("test_003")
        
if __name__ == '__main__':
    kuto.main()
```

* 被依赖的用例需要用name定义被依赖的名称，因为本装饰器是基于pytest.mark.dependency，它会出现识别不了被装饰的方法名的情况
  ，所以通过name强制指定最为准确
  ```@depend(name='test_001')```
* `test_002` 依赖于 `test_001` , `test_003`又依赖于`test_002`。当被依赖的用例，错误、失败、跳过，那么依赖的用例自动跳过。
* 如果依赖多个用例，传入一个list即可
```@depend(['test_001', 'test_002'])```
  
### 发送邮件

```python
import kuto
from kuto.utils.mail import Mail


if __name__ == '__main__':
    kuto.main()
    mail = Mail(host='xx.com', user='xx@xx.com', password='xxx')
    mail.send_report(title='Demo项目测试报告', report_url='https://www.baidu.com', receiver_list=['xx@xx.com'])
```

- title：邮件标题
- report_url: 测试报告的url
- receiver_list: 接收报告的用户列表


### 发送钉钉

```python
import kuto
from kuto.utils.dingtalk import DingTalk


if __name__ == '__main__':
    kuto.main()
    dd = DingTalk(secret='xxx',
                  url='xxx')
    dd.send_report(msg_title='Demo测试消息', report_url='https://www.baidu.com')
```

- `secret`: 如果钉钉机器人安全设置了签名，则需要传入对应的密钥。
- `url`: 钉钉机器人的Webhook链接
- `msg_title`: 消息标题
- `report_url`: 测试报告url

## 数据驱动

数据驱动是测试框架非常重要的功能之一，它可以有效的节约大量重复的测试代码。kuto针对该功能做强大的支持。

### @data()方法

当测试数据量比较少的情况下，可以通过`@data()`管理测试数据。

# Web UI 测试

## 浏览器与驱动

### 下载浏览器驱动

> kuto集成webdriver_manager管理浏览器驱动。
和Selenium一样，在使用kuto运行自动化测试之前，需要先配置浏览器驱动，这一步非常重要。

kuto 集成 [webdriver_manager](https://github.com/SergeyPirogov/webdriver_manager) ，提供了`chrome/firefox/edge`浏览器驱动的自动下载。

__自动下载__

如果你不配置浏览器驱动也没关系，kuto会根据你使用的浏览器版本，自动化下载对应的驱动文件。

kuto 检测到的`Chrome`浏览器后，自动化下载对应版本的驱动，并保存到本地，以便于下次执行的时候就不需要下载了。
并且，非常贴心的将`chromedriver`的下载地址从 google 切换成了 taobao 的镜像地址。

__手动下载__

通过`kuto`命令下载浏览器驱动。
```shell
> kuto --install chrome
> kuto --install firefox
> kuto --install ie
> kuto --install edge
```
1. 默认下载到当前的`C:\Users\username\.wdm\drivers\` 目录下面。
2. Chrome: `chromedriver` 驱动，众所周知的原因，使用的taobao的镜像。
3. Safari: `safaridriver` （macOS系统自带，默认路径:`/usr/bin/safaridriver`）

指定本地浏览器驱动

```python
import kuto
from kuto import ChromeConfig


if __name__ == '__main__':
    ChromeConfig.command_executor = '/Users/UI/Documents/chromedriver'
    kuto.main(platform='web', browser="chrome")
```

在`main()`方法中通过`browser`参数设置不同的浏览器，默认为`Chrome`浏览器。

## API

### 查找元素

* id_
* name
* className
* tag
* linkText
* partialLinkText
* css
* xpath

__帮助信息__

* [CSS选择器](https://www.w3school.com.cn/cssref/css_selectors.asp)
* [xpath语法](https://www.w3school.com.cn/xpath/xpath_syntax.asp)

# APP UI 测试

## 公共依赖

* [weditor](https://github.com/alibaba/web-editor)
  - 用于查看控件属性
    
* 手机通过usb连接电脑

## 安卓 UI 测试

### 依赖环境

* [adb](https://formulae.brew.sh/cask/android-platform-tools)
    - 用于查看手机设备id
    
### API

#### 查找元素

* resourceId
* className
* text
* xpath

## IOS UI 测试

### 依赖环境

* [WebDriverAgent](https://testerhome.com/topics/7220)
    - 把代码操作转化成原生操作
* [tidevice](https://github.com/alibaba/taobao-iphone-device)
    - 查看手机设备id
    - 启动WebDriverAgent
    
### API

#### 查找元素

* name
* label
* value
* text
* className
* xpath

