import mysql.connector
import json
from mysql.connector import Error

# db_config.json 파일에서 DB 정보 읽기
def load_db_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

# 데이터베이스 연결 및 테이블 생성
def create_table_from_config(config_file):
    try:
        # DB 정보 로드
        db_config = load_db_config(config_file)

        # 데이터베이스 연결
        connection = mysql.connector.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )

        if connection.is_connected():
            print("Database connected successfully")

            # 테이블 생성 SQL 실행
            create_table_query = """
            CREATE TABLE IF NOT EXISTS status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                fog BOOLEAN NOT NULL,
                plasma BOOLEAN NOT NULL,
                pump BOOLEAN NOT NULL
            )
            """

            cursor = connection.cursor()
            cursor.execute(create_table_query)
            print("Table 'status' created successfully or already exists")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    except FileNotFoundError:
        print("db_config.json file not found.")
    except json.JSONDecodeError:
        print("Error parsing db_config.json.")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

# 실행
if __name__ == "__main__":
    create_table_from_config("db_config.json")
