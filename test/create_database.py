import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 및 테이블 생성
def create_table_from_env():
    try:
        # .env에서 DB 정보 로드
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", 3306)  # 기본 포트 3306
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        if not all([db_host, db_user, db_password, db_name]):
            print("Error: Missing required database configuration in .env file.")
            return

        # 데이터베이스 연결
        connection = mysql.connector.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            database=db_name
        )

        if connection.is_connected():
            print("Database connected successfully")

            # 테이블 생성 SQL 실행
            create_table_query = """
            CREATE TABLE IF NOT EXISTS power_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                fog BOOLEAN NOT NULL,
                plasma BOOLEAN NOT NULL,
                pump BOOLEAN NOT NULL,
                description TEXT NOT NULL
            )
            """

            cursor = connection.cursor()
            cursor.execute(create_table_query)
            print("Table 'power_status' created successfully or already exists")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

# 실행
if __name__ == "__main__":
    create_table_from_env()
