---
name: email-sender
description: 邮件发送工具。使用 QQ 邮箱 yyf050413@qq.com 发送邮件到任何邮箱地址。当用户要求发送邮件、发 email、给某人发消息、发送通知时使用。支持发送到 Gmail、Outlook、QQ、163、公司邮箱等任何有效邮箱地址。
---

# 邮件发送工具 (QQ邮箱)

使用 QQ 邮箱 **yyf050413@qq.com** 发送邮件到任何邮箱地址。

## 功能

- ✅ 使用 QQ 邮箱发送邮件到任何邮箱
- ✅ 支持自定义主题和内容
- ✅ 支持纯文本和 HTML 格式邮件
- ✅ SSL 加密连接

## 使用方法

### 发送邮件

```bash
python3 scripts/send_email.py <收件人邮箱> <主题> <内容>
```

### 示例

```bash
# 发送到 Gmail
python3 scripts/send_email.py someone@gmail.com "Hello" "邮件内容"

# 发送到 Outlook
python3 scripts/send_email.py user@outlook.com "通知" "请查收"

# 发送到 QQ 邮箱
python3 scripts/send_email.py 123456@qq.com "问候" "你好"

# 发送 HTML 格式邮件
python3 scripts/send_email.py user@example.com "测试" "<h1>标题</h1><p>内容</p>"
```

### 测试配置

```bash
python3 scripts/send_email.py test
```

## 配置信息

| 项目 | 值 |
|------|-----|
| 发件人邮箱 | yyf050413@qq.com |
| SMTP 服务器 | smtp.qq.com |
| 端口 | 465 (SSL) |
| 加密方式 | SSL |

配置会自动保存到 `~/.qq_email_config.json`

## ⚠️ 你需要提供

### 1. QQ 邮箱授权码

**这不是你的 QQ 登录密码！**

获取步骤：
1. 登录 https://mail.qq.com
2. 设置 → 账户 → 开启 POP3/SMTP 服务
3. 按提示发送短信验证
4. 获得 **16 位授权码**（格式如: `abcdabcdabcdabcd`）

### 2. 首次运行配置

第一次使用时会自动提示输入授权码：
```bash
python3 scripts/send_email.py test
# 按提示输入授权码
```

或者手动创建配置文件：
```bash
cat > ~/.qq_email_config.json << 'EOF'
{
  "email": "yyf050413@qq.com",
  "password": "你的授权码"
}
EOF
chmod 600 ~/.qq_email_config.json
```

## 故障排查

如果发送失败，请检查：

1. **确认使用授权码** - 不是 QQ 登录密码
2. **确认 SMTP 已开启** - 在 QQ 邮箱设置中确认
3. **检查网络连通性** - 确保能访问 smtp.qq.com:465

## 依赖

- Python 3.x
- 标准库: smtplib, email, json

无需额外安装第三方包。

## 安全提示

- 配置文件 `~/.qq_email_config.json` 权限设为 600（仅所有者可读）
- 不要将授权码提交到 Git 仓库
- 如果授权码泄露，立即到 QQ 邮箱设置中重新生成
