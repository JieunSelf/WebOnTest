import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'class.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 파일 업로드 용량 제한 단위: 바이트
MAX_CONTENT_LENGTH = 16*1024*1024

