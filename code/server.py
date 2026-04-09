# server.py 电脑端运行
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# 初始化SQLite数据库
def init_db():
    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    # 创建表：id(自增), 时间戳, 温度值, 设备名
    c.execute('''CREATE TABLE IF NOT EXISTS temp_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  temperature REAL NOT NULL,
                  device TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# 插入数据到数据库
def insert_temp(temp, device="M5StickCPlus"):
    conn = sqlite3.connect('temperature.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO temp_data (timestamp, temperature, device) VALUES (?, ?, ?)",
              (timestamp, temp, device))
    conn.commit()
    conn.close()

# 接收数据的接口
@app.route('/upload_temp', methods=['POST'])
def upload_temp():
    try:
        data = request.get_json()
        temp = data.get('temperature')
        if temp is None:
            return jsonify({"status": "error", "msg": "Missing temperature"}), 400
        
        # 存入SQLite
        insert_temp(temp)
        print(f"✅ 收到数据: 温度={temp}°C，已存入数据库")
        return jsonify({"status": "success", "msg": "Data saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == '__main__':
    init_db()
    # 监听电脑的局域网IP，端口5000，0.0.0.0允许局域网内设备访问
    app.run(host='0.0.0.0', port=5000, debug=False)