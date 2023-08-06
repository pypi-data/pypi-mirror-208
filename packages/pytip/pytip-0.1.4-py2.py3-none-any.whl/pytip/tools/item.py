import re
import string
import random
import datetime
import itertools


REGEX_DATETIME = {
    '[\d]{4}-[\d]{2}-[\d]{2}.[A-Z]{2}[\d]{1,2}:[\d]{1,2}:[\d]{1,2}':
    '%Y-%m-%d.%p%I:%M:%S', # '2022-07-31.AM3:02:30'
    '[\d]{4}\.[\d]{2}\.[\d]{2}\.[A-Z]{2}[\d]{1,2}:[\d]{1,2}':
    '%Y.%m.%d.%p%I:%M',    # '2022.07.31.AM3:02',
    "^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}":
    '%Y/%m/%d %H:%M:%S',    # '2023/03/28 10:40:00',
}


# Input params 전처리 작업용
def date_to_string(
        date:any=None, 
        only_number:bool=False,
        datetime_obj:bool=False,
        business_day:bool=False,
    ):

    r"""date 객체를 string 으로 자동변환
    _date        : 날짜객체
    only_number  : 날짜 구분자 없이 숫자로만 출력 
    datetime_obj : datetime 객체로 출력
    business_day : 주말 -> 해당 주차 평일로 변환"""

    _return = None
    if date is None:
        _return = datetime.date.today().isoformat()
    elif type(date) == datetime.date:
        _return = date.isoformat()
    elif type(date) == datetime.datetime:
        _return = date.date().isoformat()
    elif type(date) == str:
        _check = "".join(re.findall(r'[\d]{8}', date))
        _check_re = re.findall('[,-//.]', date)
        if len(_check) == 8:
            _return = f"{_check[:4]}-{_check[4:6]}-{_check[6:]}"

        elif len(_check_re) > 0:
            for punct_string in ['-','/',',', '.']:
                if date.find(punct_string) != -1:
                    _return = "-".join(list(map(
                        lambda x : (f'{x:0>2}'), date.split(punct_string)))
                    )
                else:
                    pass

    assert _return is not None, f'TypeError : {date} 를 분석할 수 없습니다'
    # datetime.datetime.strptime('09/19/22 13:55:26', '%m/%d/%y %H:%M:%S')
    if business_day:
        _return = datetime.datetime.strptime(_return, '%Y-%m-%d').date()
        if (_return.weekday() - 4) > 0: # 주말일 때만 해당함수 적용
            _return = _return - datetime.timedelta(_return.weekday() - 4)
        _return = _return.isoformat()
    if only_number:
        _return = _return.replace('-','')
    if datetime_obj:
        _return = datetime.datetime.strptime(_return, '%Y-%m-%d').date()
    return _return


# 텍스트를 datetime 객체로 해석 (REGEX_DATETIME)
def string_to_datetime(text:str):
    r"""text -> datetime.str
    regex 추출값에 따라 `time regex format` 개별적용"""

    format = ''
    time_regex = REGEX_DATETIME
    for regex, time_string in time_regex.items():
        check = re.findall(regex, text)
        if len(check) > 0:
            format = time_string

    # regex 분석결과 없을 때, 원본 그대로 출력
    if format == '':
        return text
    return datetime.datetime.strptime(text, format)


# items to split lists
def divide_chunks(items:list=None, n:int=None):
    r"""Split items
    (list) items : 객체 나누기
    (int)  n : Number"""
    if type(items) == list:
        for i in range(0, len(items), n): # looping till length l
            yield items[i:i + n]          # list should have
    
    elif type(items) == dict:
        for i in range(0, len(items), n):
            yield dict(itertools.islice(items.items(), i ,i+n))


# 문자 난수생성 (비밀번호 생성기)
def password(length:int=12) -> str:
    r"""난수문자 생성기 (ex> 비밀번호)
    length : 생성문자 길이"""
    letters = string.ascii_letters + string.digits + "!#$%&*+-?@" # string.punctuation
    return "".join([random.choice(letters)  for _ in range(length)])
