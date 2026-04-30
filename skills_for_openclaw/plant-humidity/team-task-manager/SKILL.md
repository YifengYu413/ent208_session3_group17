---
name: team-task-manager
description: ENT 团队任务管理系统。支持任务分配、进度跟踪、邮件通知、下一步建议生成。数据存储在 ~/.openclaw/projects/ent/ 目录下，包括 team.json（团队配置）和 tasks.csv（任务表格）。当用户提到任务分配、团队进度、下一步做什么、发送任务通知时使用。
---

# 🎯 ENT 团队任务管理系统

团队级数字员工的核心协作 Skill。

## 数据文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 团队配置 | `~/.openclaw/projects/ent/team.json` | 成员信息、邮箱、角色 |
| 任务表格 | `~/.openclaw/projects/ent/tasks.csv` | 所有任务的状态和进度 |

## 功能

### 1. 任务看板

```bash
python3 scripts/task_manager.py list
```

可选筛选：
```bash
python3 scripts/task_manager.py list --status 进行中
python3 scripts/task_manager.py list --member Yifeng
```

### 2. 添加任务

```bash
python3 scripts/task_manager.py add "任务名" "描述" "负责人" "截止日期" [优先级]
```

示例：
```bash
python3 scripts/task_manager.py add "设计PPT模板" "准备展示PPT" "E" "2026-05-10" 高
```

### 3. 更新进度

```bash
python3 scripts/task_manager.py progress <id> <百分比> [状态]
```

示例：
```bash
python3 scripts/task_manager.py progress 3 100 已完成
python3 scripts/task_manager.py progress 5 80
```

### 4. 更新任务属性

```bash
python3 scripts/task_manager.py update <id> --<字段> <值>
```

示例：
```bash
python3 scripts/task_manager.py update 5 --assigned_to Jiayi
python3 scripts/task_manager.py update 2 --deadline 2026-05-12
```

### 5. 发送任务通知

**分配新任务时通知成员：**
```bash
python3 scripts/task_manager.py notify <id>
```

**发送进度提醒：**
```bash
python3 scripts/task_manager.py remind <id> "请尽快完成前端部分"
```

### 6. 下一步建议

```bash
python3 scripts/task_manager.py next
```

自动分析所有任务状态，生成行动建议：
- 紧急任务（3天内截止）
- 未分配任务
- 进度慢的提醒
- 整体完成率

### 7. 周汇总报告

```bash
python3 scripts/task_manager.py summary
```

## 典型工作流程

**场景 1：分配新任务**
```
用户：给 Jiayi 分配一个设计 Logo 的任务，5月5号截止
AI：
  1. 添加任务
     python3 task_manager.py add "设计Logo" "团队Logo设计" "Jiayi" "2026-05-05" 高
  2. 发送邮件通知
     python3 task_manager.py notify 9
  3. 汇报结果
```

**场景 2：更新进度**
```
用户：任务3完成了
AI：
  1. 更新进度
     python3 task_manager.py progress 3 100 已完成
  2. 展示最新看板
     python3 task_manager.py list
```

**场景 3：下一步建议**
```
用户：我们接下来该做什么？
AI：
  1. 分析任务状态
     python3 task_manager.py next
  2. 根据建议给出行动方案
```

**场景 4：周会汇总**
```
用户：生成周汇总
AI：
  1. 生成汇总文本
     python3 task_manager.py summary
  2. 发送给所有成员（或展示）
```

## 注意事项

- 日期格式：`YYYY-MM-DD`
- 优先级：高 / 中 / 低
- 状态：待开始 / 进行中 / 已完成
- 进度：自动推断状态，也可手动指定

## 依赖

- Python 3.x
- 标准库：csv, json, os, datetime
- email-sender skill（用于邮件通知）
