#!/usr/bin/env python3
"""
QQ 邮箱邮件发送工具
适用于 yyf050413@qq.com

⚠️ 重要提示:
QQ 邮箱需要使用"授权码"而不是登录密码！
获取方式:
1. 登录 https://mail.qq.com
2. 设置 → 账户 → 开启 POP3/SMTP 服务
3. 生成授权码（16位字符串）
"""

import smtplib
import os
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# ============ 默认配置 ============
DEFAULT_FROM_EMAIL = 'yyf050413@qq.com'
DEFAULT_FROM_NAME = '大圣助手'

# 配置文件路径
CONFIG_FILE = os.path.expanduser('~/.qq_email_config.json')

# ============ QQ SMTP 配置 ============
QQ_SMTP_SSL = {
    'server': 'smtp.qq.com',
    'port': 465,
    'use_ssl': True,
    'use_tls': False,
    'description': 'QQ邮箱 SMTP (SSL)'
}

QQ_SMTP_TLS = {
    'server': 'smtp.qq.com',
    'port': 587,
    'use_ssl': False,
    'use_tls': True,
    'description': 'QQ邮箱 SMTP (TLS)'
}


def load_config():
    """加载邮箱配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 配置文件读取失败: {e}")
    return None


def save_config(email, password):
    """保存邮箱配置"""
    config = {
        'email': email,
        'password': password,
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        os.chmod(CONFIG_FILE, 0o600)
        print(f'✓ 配置已保存到: {CONFIG_FILE}')
        return True
    except Exception as e:
        print(f'✗ 配置保存失败: {e}')
        return False


def setup_config():
    """交互式配置邮箱"""
    print("=" * 70)
    print("📧 QQ 邮箱配置")
    print("=" * 70)
    print(f"发件人: {DEFAULT_FROM_EMAIL}")
    print("\n⚠️ 你需要提供 QQ 邮箱授权码 (不是登录密码！)")
    print("   获取方式: https://mail.qq.com → 设置 → 账户 → 开启SMTP")
    print("=" * 70)
    
    email = DEFAULT_FROM_EMAIL
    
    existing = load_config()
    if existing and existing.get('password'):
        print(f"\n检测到已有配置: {existing['email']}")
        choice = input("是否更新授权码? [y/N]: ").strip().lower()
        if choice != 'y':
            print("使用现有配置")
            return existing
    
    password = input("\n请输入 QQ 邮箱授权码: ").strip()
    
    if not password:
        print("✗ 授权码不能为空")
        return None
    
    if save_config(email, password):
        print("\n✓ 配置完成！")
        return load_config()
    return None


def send_email(to_email, subject, body, from_name=None):
    """发送邮件"""
    config = load_config()
    if not config or not config.get('password'):
        print("⚠️ 未检测到邮箱配置，开始初始化...")
        config = setup_config()
        if not config:
            print("✗ 配置失败，无法发送邮件")
            return False
    
    from_email = config.get('email', DEFAULT_FROM_EMAIL)
    password = config['password']
    display_name = from_name or DEFAULT_FROM_NAME
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['From'] = formataddr((display_name, from_email))
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # 判断内容类型
    if body.strip().startswith('<') or '<html>' in body.lower():
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    else:
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        html_body = f"<pre>{body}</pre>"
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # 发送 (QQ 优先 SSL)
    smtp_config = QQ_SMTP_SSL
    
    try:
        print(f"📤 正在连接 {smtp_config['server']}:{smtp_config['port']} ({smtp_config['description']})...")
        
        server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'], timeout=30)
        
        print("🔐 正在登录...")
        server.login(from_email, password)
        
        print(f"📮 正在发送邮件到 {to_email}...")
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        
        print(f"✅ 邮件发送成功！")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ 认证失败: {e}")
        print("\n💡 提示:")
        print("   1. 确认使用的是'授权码'，不是 QQ 登录密码")
        print("   2. 确认 QQ 邮箱的 SMTP 服务已开启")
        print("   3. 重新运行配置: python3 send_email.py test")
        return False
        
    except Exception as e:
        print(f"\n❌ 发送失败: {e}")
        return False


def test_config():
    """测试邮箱配置"""
    print("=" * 70)
    print("📧 QQ 邮箱配置测试")
    print("=" * 70)
    print(f"发件人: {DEFAULT_FROM_EMAIL}")
    print("SMTP: smtp.qq.com:465 (SSL)")
    print("=" * 70)
    
    config = load_config()
    if not config:
        print("\n⚠️ 未检测到配置")
        config = setup_config()
        if not config:
            return False
    
    print(f"\n✓ 已加载配置: {config['email']}")
    print(f"✓ 配置文件: {CONFIG_FILE}")
    
    # 测试连接
    try:
        print("\n🔌 测试连接...")
        server = smtplib.SMTP_SSL('smtp.qq.com', 465, timeout=10)
        print("✓ SSL 连接成功")
        
        print("🔐 测试登录...")
        server.login(config['email'], config['password'])
        print("✓ 登录成功")
        server.quit()
        
        print("\n" + "=" * 70)
        print("🎉 配置测试通过！可以发送邮件了")
        print("=" * 70)
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ 认证失败 - 授权码错误或 SMTP 未开启")
        print("\n请重新配置:")
        setup_config()
        return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == '__main__':
    test_config()
