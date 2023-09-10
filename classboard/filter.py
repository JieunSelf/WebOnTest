'''
Data 형식을 정해주는 필터 처리
2021-05-24
'''
def format_datetime(value, fmt='%Y년 %m월 %d일 %H:%M'):
    return value.strftime(fmt)