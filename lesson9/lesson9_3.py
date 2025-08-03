#請幫我自訂一個function
#連線至postgres DB
#建立連線環境參數的樣版
import psycopg2
#請幫我建立一個function
#傳入connection參數
#建立一個cursor
#執行SQL查詢
#並回傳查詢結果

def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

def create_connection():
    conn = psycopg2.connect(
        host="host.docker.internal",  # 使用 Docker 的內部主機名
        port="5432",  # PostgreSQL 的預設端口
        database="postgres",
        user="postgres",
        password="raspberry"
    )
    return conn

def main():
    conn = create_connection()
    if conn:
        print("成功連接到資料庫！")
        query = """
        SELECT count(*) AS "筆數"
        FROM "台鐵車站資訊";
        """
        result = execute_query(conn, query)
        print("台鐵車站資訊：", result)
        conn.close()
    else:
        print("無法連接到資料庫，請檢查設定。")
        return
    
if __name__ == "__main__":
    main()
#這個程式碼片段建立了一個連線到 PostgreSQL 資料庫的函數 `create_connection`，並在 `main` 函數中測試
#連線是否成功。你可以根據需要修改主機、端口、資料庫名稱、使用者和密碼等參數。
#確保在執行此程式碼之前已經安裝了 `psycopg2` 庫，可以使用以下命令安裝：
#```bash
#pip install psycopg2
#```