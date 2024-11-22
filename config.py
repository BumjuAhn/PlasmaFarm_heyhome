import os
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# 공통 로깅 설정
LOG_FILE = "log_file.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 공통 환경 변수
BASE_URL = os.getenv("BASE_URL")
DEVICE_ID = os.getenv("DEVICE_ID")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}
