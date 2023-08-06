import os
import json
import datetime
import termcolor
import http.client as httplib
from urllib import request


def check_ip(url="http://ip.jsontest.com"):

    r"""인터넷 접속확인
    :: return :: True / False"""
    response = request.urlopen(url).read()
    try:
        response = json.loads(response)
        return response['ip']
    except Exception as E:
        print(termcolor.colored(E, 'red'))
        return None


# Cache file Check 함수
def check_folder_file(file:str=None, folder:str=None):
    r"""파일과 폴더 존재여부 확인 (폴더가 없으면 해당 폴더를 생성)
    file (str) : 파일이름
    folder (str) : 폴더명
    :: return :: Boolean, file_path"""
    assert folder is not None, "확인할 folder 를 지정하지 않았습니다."
    str_folder = os.path.abspath(os.path.join(folder, ''))

    # Check Folder 
    if not os.path.exists(str_folder):
        os.makedirs(str_folder)

    # Check File (생성 날짜가 동일한지 확인)
    file_name = os.path.abspath(os.path.join(folder, file))
    if os.path.exists(file_name) == True:
        file_creation_date = datetime.datetime.fromtimestamp(os.path.getatime(file_name)).date()
        if file_creation_date == datetime.datetime.today().date():
            return True, file_name
    
    return False, file_name


# 터미널 메세지 출력기
# http://www.dreamy.pe.kr/zbxe/CodeClip/165424
class Message:
    r"""Text Message Color"""
    # grey, red, green, yellow, blue, magenta, cyan, white
    def __repr__(self): 
        return """Text 내용을 상황별 칼라로 출력\n[process, done, alert, warning]"""

    def __new__(cls, text:str=''):
        cls.text = text
        return super().__new__(cls)

    @property
    def process(self):
        text = "<"*3 + "  " + self.text + "  " + "<"*5
        termcolor.cprint(self.text, 'magenta')

    @property
    def done(self):
        text = ">"*10 + "  " + self.text + "  " + "<"*10
        termcolor.cprint(text, 'cyan')

    @property
    def alert(self):
        text = "!"*5 + "  " + self.text + "  " + "!"*5
        termcolor.cprint(text, 'red')

    @property
    def warning(self):
        text = "!"*3 + "  " + self.text + "  " + "."*3
        termcolor.cprint(text, 'grey')

