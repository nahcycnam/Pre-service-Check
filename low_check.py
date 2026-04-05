import requests, re, warnings
from bs4 import BeautifulSoup
from datetime import datetime, time as dt_time, timedelta  # 重命名time
import msvcrt
import time as time_module  # 重命名time模块
import webbrowser, os
from PyQt6.QtWidgets import (QApplication, QMessageBox, QDialog,
                             QVBoxLayout, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt
import sys


class LMIS:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"}
        self.maximo_url = "http://lmis-maximo.subway.com/maximo/ui/maximo.jsp"

    def get_loginstamp(self):
        r = self.session.get(url='http://lmis-maximo.subway.com/maximo/ui/login', headers=self.headers)
        # 假设html_content是你的HTML内容
        soup = BeautifulSoup(r.text, 'lxml')

        # 通过id查找
        loginstamp_input = soup.find('input', {'id': 'loginstamp'})
        self.loginstamp = loginstamp_input.get('value')
        # print(f'loginstamp: {self.loginstamp}')

    def login(self):
        # 登录
        r = self.session.post(
            'http://lmis-maximo.subway.com/maximo/ui/login',
            headers=self.headers,
            data={
                "login": "jsp",
                "loginstamp": self.loginstamp,
                "username": "taojin",
                "password": "Tjz83157008$",
            }
        )

        soup = BeautifulSoup(r.text, 'lxml')
        csrftoken = soup.find('input', attrs={"id": "csrftokenholder"})['value']
        self.csrftoken = csrftoken
        userfullname = soup.find('span', attrs={"class": "homeButtontxtappname"}).text
        self.userfullname = userfullname
        uisessionid = soup.find('input', attrs={"id": "uisessionid"})['value']
        self.uisessionid = uisessionid
        welcome_span = soup.find('span', id='txtappname')
        text = welcome_span.get_text(strip=True)
        print(f'{text}\n')  # 输出："欢迎，淘金站"

    def loadapp(self):
        # 工单跟踪
        url = f'http://lmis-maximo.subway.com/maximo/ui/?event=loadapp&value=wotrack&uisessionid={self.uisessionid}&csrftoken={self.csrftoken}'
        r = self.session.get(url=url, headers=self.headers)
        # print(r.text)

    def click_mx93(self):
        # 点击下拉映像
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                "uisessionid": self.uisessionid,
                "csrftoken": self.csrftoken,
                "currentfocus": "mx92",
                "events": '[{"type":"click","targetId":"mx93","value":"","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]',
            }
        )
        # print(r.text)

    def get_wotrack(self):
        # 本日运营前检查
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx92',
                'events': '[{"type":"click","targetId":"wotrack_mainrec_menus","value":"0_本日运营前检查_query","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )

        # print(r.text)
        # 方法1.3：通过class查找（更精确）
        # 更精确的过滤
        warnings.filterwarnings("ignore",
                                message="It looks like you're parsing an XML document using an HTML parser")
        soup = BeautifulSoup(r.text, 'lxml')
        work_order_span = soup.find('span', class_='text txtbold text label label anchor')
        work_order = work_order_span.get_text().strip()

        # 使用正则表达式匹配class
        description_label = soup.find('label', class_=re.compile(r'text.*label'))
        description = description_label.get_text(strip=True)
        print(f"工单: {work_order}\t{description}\n")

    def click_mx329(self):
        # 工序填报
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx92',
                'events': '[{"type":"click","targetId":"mx329","value":"","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        print("工序填报：")

    def setvalue_mx2784_R0(self):
        # 到岗人数
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2804[R:0]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:0]","value":"3","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # 使用正则表达式匹配数字
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:0\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:0\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:0]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'到岗人数： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R1(self):
        # LOW是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2804[R:1]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:1]","value":"是，已执行取消限速命令","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:1\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:1\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:1]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'LOW是否正常： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R2(self):
        # Glink登陆是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2784[R:3]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:2]","value":"是","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:2\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:2\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:2]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'Glink登陆是否正常： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R3(self):
        # 站台门状态是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2784[R:4]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:3]","value":"是","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:3\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:3\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:3]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'站台门状态是否正常： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R4(self):
        # 线路出清是否出清
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2784[R:5]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:4]","value":"是","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:4\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:4\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:4]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'线路出清是否出清： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R5(self):
        # 无线电台是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2804[R:5]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:5]","value":"是","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:5\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:5\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:5]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'无线电台是否正常： {result}\t{recorder}\t{extracted_time}')

    def click_mx1612(self):
        # 下一工单
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx1612',
                'events': '[{"type":"click","targetId":"mx1612","value":"true","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # if "上一页 [CTRL+向左箭头]" in r.text:
        #     print('下一页')

    def setvalue_mx2784_R6(self):
        # 软管灯是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2787[R:7]_1',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:6]","value":"是","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"},{"type":"click","targetId":"mx2780[R:7]","value":"","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}' + ']'
            },
        )

        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:6\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:6\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:6]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'软管灯是否正常： {result}\t{recorder}\t{extracted_time}')

    def setvalue_mx2784_R7(self):
        # 道岔钩锁是否正常
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx2804[R:7]',
                'events': '[{"type":"setvalue","targetId":"mx2784[R:7]","value":"无此项设备","requestType":"ASYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        # 假设你的HTML在变量html_content中
        soup = BeautifulSoup(r.text, 'lxml')

        # 工序结果
        pattern = r'id="mx2784\[R:7\]".*?title="工序结果：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        result = match.group(1)

        # 记录人
        pattern = r'id="mx2816\[R:7\]".*?title="记录人：\s*([^"]+)"'
        match = re.search(pattern, r.text, re.DOTALL)
        recorder = match.group(1)

        # 记录时间
        input_tag = soup.find('input', id='mx2828[R:7]')
        title = input_tag['title']
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(time_pattern, title)
        extracted_time = match.group(0)

        print(f'道岔钩锁是否正常： {result}\t{recorder}\t{extracted_time}\n')

    def click_mx318(self):
        # 工单
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx318_anchor',
                'events': '[{"type":"click","targetId":"mx318","value":"","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # if "[R:7]" not in r.text:
        #     print("工单")

    def setvalue_mx4253(self):
        # 实际开始时间
        # 获取当前日期时间
        now = datetime.now()
        # 减5秒
        time_minus_15m = now - timedelta(minutes=15)
        # 格式化输出
        result = time_minus_15m.strftime("%Y-%m-%d %H:%M:%S")

        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx4261',
                'events': '[{"type":"setvalue","targetId":"mx4253","value":"' + result + '","requestType":"ASYNC","processvalue":"' + result + '","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        # print(r.text)
        soup = BeautifulSoup(r.text, 'lxml')
        # 找到 input 元素
        input_element = soup.find('input', {'id': 'mx4253'})  # 或者用其他属性定位
        # 方法1：使用正则表达式提取时间
        title = input_element.get('title', '')
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', title)
        time_str = match.group(1)
        print(f'实际开始时间：{time_str}')  #

    def setvalue_mx4261(self):
        # 实际完成时间
        # 获取当前日期时间
        now = datetime.now()
        # 减5秒
        time_minus_5s = now - timedelta(seconds=5)
        # 格式化为字符串
        time_str = time_minus_5s.strftime("%Y-%m-%d %H:%M:%S")

        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx4281',
                'events': '[{"type":"setvalue","targetId":"mx4261","value":"' + time_str + '","requestType":"ASYNC","processvalue":"' + time_str + '","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        soup = BeautifulSoup(r.text, 'lxml')
        # 找到 input 元素
        input_element = soup.find('input', {'id': 'mx4261'})  # 或者用其他属性定位
        # 方法1：使用正则表达式提取时间
        title = input_element.get('title', '')
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', title)
        time_str = match.group(1)
        print(f'实际完成时间：{time_str}\n')  #

    def save(self):
        # 到岗人数
        r = self.session.post(
            url=self.maximo_url,
            headers=self.headers,
            data={
                'uisessionid': self.uisessionid,
                'csrftoken': self.csrftoken,
                'currentfocus': 'mx3686[R:0]',
                'events': '[{"type":"click","targetId":"mx363","value":"","requestType":"SYNC","csrftokenholder":"' + self.csrftoken + '"}]'
            },
        )
        soup = BeautifulSoup(r.text, 'lxml-xml')

        # 查找包含showMessage的组件
        component = soup.find('component', id='mx28_holder')
        if component:
            cdata = component.string
            if cdata:
                inner_soup = BeautifulSoup(cdata, 'html.parser')
                script = inner_soup.find('script')
                if script:
                    js_content = script.string.strip()

                    # 使用正则表达式提取消息内容
                    pattern = r'showMessage\([^,]+,\s*"([^"]+)"'
                    match = re.search(pattern, js_content)
                    if match:
                        message = match.group(1)
                        print(message)
                        print()
                        # 输出: BMXAA4205I - 记录已保存。

    def main(self):
        try:
            self.get_loginstamp()
            self.login()  # 登录
            self.loadapp()  # 工单跟踪
            self.click_mx93()  # 点击下拉映像
            self.get_wotrack()  # 本日运营前检查
            self.click_mx329()  # 工序填报
            self.setvalue_mx2784_R0()  # 到岗人数
            self.setvalue_mx2784_R1()  # LOW是否正常
            self.setvalue_mx2784_R2()  # Glink登陆是否正常
            self.setvalue_mx2784_R3()  # 站台门状态是否正常
            self.setvalue_mx2784_R4()  # 线路出清是否出清
            self.setvalue_mx2784_R5()  # 无线电台是否正常
            self.click_mx1612()  # 下一页
            self.setvalue_mx2784_R6()  # 软管灯是否正常
            self.setvalue_mx2784_R7()  # 道岔钩锁是否正常
            self.click_mx318()  # 工单
            self.setvalue_mx4253()  # 实际开始时间
            self.setvalue_mx4261()  # 实际完成时间
            self.save()  # 保存
        except Exception as e:
            # 显示错误弹窗
            error_app = QApplication.instance() or QApplication([])
            msg_box = QMessageBox()
            msg_box.setWindowTitle("错误")
            msg_box.setText("LMIS系统自动录入失败！")
            msg_box.setInformativeText("请人工录入运营前检查报表。\n错误信息：" + str(e))
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()

            print("\n\n程序执行出错，请查看错误信息")
            print("错误详情：", str(e))
            print("按任意键退出...")
            msvcrt.getch()  # 获取一个按键
            sys.exit(1)


class FRPT:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }

    def get_Sessionid(self):
        url = 'http://frpt.gzmetro.com/webroot/decision/view/report?viewlet=02_LMIS/%5B751f%5D%5B4ea7%5D%5B6548%5D%5B7387%5D%5B5206%5D%5B6790%5D/%5B8fd0%5D%5B8425%5D%5B524d%5D%5B68c0%5D%5B67e5%5D%5B62a5%5D%5B8868%5D.cpt'
        response = self.session.get(
            url=url,
            headers=self.headers,
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script', type='text/javascript')

        for script in scripts:
            if script.string:
                content = script.string

                pattern1 = r"this\.currentSessionID\s*=\s*'([a-f0-9-]+)'"
                match1 = re.search(pattern1, content)
                if match1:
                    # print(match1.group(1))
                    self.headers = {
                        'Sessionid': match1.group(1)
                    }

    def get_html(self):
        # 获取当前日期时间
        now = datetime.now()
        # 减一天
        time_minus_1d = now - timedelta(days=1)
        # 格式化为字符串
        time_str = time_minus_1d.strftime("%Y-%m-%d")
        url = "http://frpt.gzmetro.com/webroot/decision/view/report?op=fr_dialog&cmd=parameters_d"
        data = {
            "__parameters__": '{"LABEL1":"(6:00-[6b21][65e5]5:59,[6309][4f5c][4e1a][65e5][671f])","LABEL0":"[8fd0][8425][524d][68c0][67e5][60c5][51b5][6c47][603b][8868]","BEGINDATE":"' + time_str + '","LABELBEGINDATE":"[5386][53f2][6570][636e][67e5][8be2][ff1a]","LINE":"[4e94][53f7][7ebf]","LABELLINE":"[7ebf][8def][ff1a]"}',
            "_": str(time_module.time_ns())
        }
        response = self.session.post(
            url=url,
            headers=self.headers,
            data=data,
        )
        print(response.text)

        url = "http://frpt.gzmetro.com/webroot/decision/view/report"
        params = {
            '_': str(time_module.time_ns()),
            '__boxModel__': 'true',
            'op': 'page_content',
            'pn': '1',
            '__webpage__': 'true',
            '_paperWidth': '877',
            '_paperHeight': '780',
            '__fit__': 'false'
        }
        response = self.session.get(
            url,
            params=params,
            headers=self.headers,
        )
        # 输出响应
        return response.json()

    def save_styled_html(self, html_content, output_file=r'D:\运营前检查报表.html'):
        """保存带有完整样式的HTML"""
        # 完整的HTML模板
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>运营前检查报表</title>
            <style>
                .b1{{
                    border: 1px solid black;
                }}
                .pl2{{
                    padding-left: 2px;
                }}
                .tac{{
                    text-align: center;
                }}
                .fwb{{
                    font-weight: bold;
                }}
                .fh{{
                    overflow: hideen;
                    padding: 0;
                    vertical-align: middle;
                    font-size: 9pt;
                    font-family: SimSun;
                }}
                .bw{{
                    word-break: break-word;
                }}
                td{{
                    display: table-cell;
                    unicode-bidi: isolate;
                }}
                .x-table {{                
                    table-layout: fixed;
                    border-collapse: collapse;
                }}
                table {{
                    border-collapse: separate;
                    text-indent: initial;
                    border-spacing: 2px;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # 假设html_template包含你的HTML内容
        soup = BeautifulSoup(html_template, 'html.parser')

        # 查找并删除id在"r-35-0"到"r-49-0"范围内的tr元素
        # 注意：id格式是 r-{数字}-{数字}，我们需要匹配35-49的第一个数字

        # 方法1：使用正则表达式匹配id范围
        for tr in soup.find_all('tr'):
            tr_id = tr.get('id')
            if tr_id:
                # 使用正则表达式提取数字
                match = re.search(r'r-(\d+)-\d+', tr_id)
                if match:
                    num = int(match.group(1))
                    # 如果数字在35到49之间（包含），则删除
                    if 35 <= num <= 49:
                        tr.decompose()

        # 获取处理后的HTML
        new_html_template = str(soup)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_html_template)

        print(f"已保存：{output_file}")

    def open_html(self, output_file=r"D:\运营前检查报表.html"):
        # 自动在浏览器中打开
        abs_path = 'file://' + output_file
        webbrowser.register('qaxbrowser', None, webbrowser.BackgroundBrowser(
            r"C:\Users\taojinzhan\AppData\Local\Qaxbrowser\Application\qaxbrowser.exe"))
        webbrowser.get('qaxbrowser').open(abs_path)
        # 删除文件
        time_module.sleep(4)
        os.remove(output_file)


class PasswordDialog(QDialog):
    """密码输入对话框"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("密码验证")
        self.setFixedSize(200, 150)

        layout = QVBoxLayout()

        self.label = QLabel("请输入密码:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        self.submit_button = QPushButton("确认")
        self.submit_button.clicked.connect(self.check_password)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.password_correct = False

    def check_password(self):
        password = self.password_input.text()
        if password == "33":
            self.password_correct = True
            self.accept()
        else:
            self.error_label.setText("密码错误，请重新输入")
            self.password_input.clear()


# 修改原有的if __name__ == '__main__':部分
if __name__ == '__main__':
    # 1. 检查时间
    now = datetime.now()
    current_time = now.time()
    allowed_start = dt_time(4, 0, 0)  # 使用重命名后的dt_time
    allowed_end = dt_time(4, 59, 59)  # 使用重命名后的dt_time

    if not (allowed_start <= current_time <= allowed_end):
        # 不在允许的时间段，显示警告
        app = QApplication(sys.argv)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("运行限制")
        msg_box.setText("当前时间段禁止运行！")
        msg_box.setInformativeText("请在4:00-4:59之间运行此程序。")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()
        sys.exit(0)

    # 2. 在允许的时间段，要求输入密码
    app = QApplication(sys.argv)
    dialog = PasswordDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted and dialog.password_correct:
        # 密码正确，继续执行
        Lmis = LMIS()
        Lmis.main()
        Frpt = FRPT()
        Frpt.get_Sessionid()
        html = Frpt.get_html()
        Frpt.save_styled_html(html["html"])
        Frpt.open_html()
    else:
        # 密码错误或取消
        msg_box = QMessageBox()
        msg_box.setWindowTitle("错误")
        msg_box.setText("密码验证失败！")
        msg_box.setInformativeText("程序将退出。")
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
        sys.exit(1)