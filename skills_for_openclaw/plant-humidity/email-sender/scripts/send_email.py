#!/usr/bin/env python3
"""
邮件发送脚本 - Email Sender (QQ邮箱版)
用法: python3 send_email.py <收件人> <主题> <内容>
使用 QQ 邮箱 yyf050413@qq.com 发送
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qq_sender import send_email, test_config

def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("邮件发送工具 - Email Sender (QQ邮箱)")
        print("=" * 70)
        print("\n用法:")
        print("  python3 send_email.py <收件人邮箱> <主题> <内容>")
        print("  python3 send_email.py test                    # 测试邮箱配置")
        print("\n示例:")
        print("  python3 send_email.py user@example.com 'Hello' '邮件内容'")
        print("\n发件人: yyf050413@qq.com")
        print("=" * 70)
        sys.exit(1)
    
    if sys.argv[1] == 'test':
        success = test_config()
        sys.exit(0 if success else 1)
    
    if len(sys.argv) < 4:
        print("错误: 参数不足")
        print("用法: python3 send_email.py <收件人邮箱> <主题> <内容>")
        sys.exit(1)
    
    to_email = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    
    try:
        success = send_email(to_email, subject, body)
        if success:
            print(f"\n✓ 邮件已成功发送至: {to_email}")
        else:
            print(f"\n✗ 邮件发送失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发送过程出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
