import os, sys, io
import M5
from M5 import *
from hardware import Pin, I2C
from unit import ENVUnit
import time
import network
import requests

# ====================== 配置区（请严格填写！）======================
WIFI_SSID = "小蜜蜂iPhone"          # 仅支持2.4G Wi-Fi，区分大小写
WIFI_PASSWORD = "yyf050413"     # 区分大小写，不要有多余空格
SERVER_URL = "http://172.20.10.3:5000/upload_temp"
# ====================================================================

# 全局变量声明
i2c0 = None
ENV = None
sensorvalue = 0.0
temp_label = None
wlan = None

# -------------------------- 优化版Wi-Fi连接函数（核心修复）--------------------------
def connect_wifi():
    global wlan
    # 1. 彻底清理Wi-Fi状态，避免驱动冲突
    if wlan is not None and wlan.active():
    wlan.disconnect()
    wlan.active(False)
    time.sleep_ms(500)  # 等待驱动释放

    # 2. 重新初始化Wi-Fi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep_ms(200)  # 等待初始化完成

    # 3. 连接Wi-Fi，增加重试机制
    max_retry = 3
    for retry in range(max_retry):
        if not wlan.isconnected():
            print(f"正在连接Wi-Fi... (第{retry+1}次尝试)")
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            # 等待连接，最长15秒
            for _ in range(15):
                if wlan.isconnected():
                    break
                time.sleep_ms(1000)
        if wlan.isconnected():
            print(f"✅ Wi-Fi连接成功! IP: {wlan.ifconfig()[0]}")
            return True
        else:
            print(f"❌ 第{retry+1}次连接失败，重试中...")
            wlan.disconnect()
            time.sleep_ms(1000)

    print("❌ Wi-Fi连接失败，已达最大重试次数")
    return False

# -------------------------- 数据上传函数（增加异常捕获）--------------------------
def upload_to_server(temp):
    global wlan
    if not wlan or not wlan.isconnected():
        print("⚠ Wi-Fi未连接，跳过本次上传")
        return False
    try:
        payload = {"temperature": round(temp, 2)}
        # 增加超时，避免卡死
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print("✅ 数据上传成功")
            return True
        else:
            print(f"❌ 数据上传失败，服务器响应: {response.status_code}")