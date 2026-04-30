#!/usr/bin/env python3
"""
🎯 ENT 团队任务管理系统
团队级数字员工核心 Skill

功能：
- 任务 CRUD（增删改查）
- 自动分配 + 邮件通知
- 进度跟踪
- 下一步建议生成
- 周汇总报告

数据文件：
- ~/.openclaw/projects/ent/team.json   (团队成员)
- ~/.openclaw/projects/ent/tasks.csv   (任务表格)
"""

import csv
import json
import os
import sys
from datetime import datetime, timedelta

# ============ 路径配置 ============
PROJECT_DIR = os.path.expanduser("~/.openclaw/projects/ent")
TEAM_FILE = os.path.join(PROJECT_DIR, "team.json")
TASKS_FILE = os.path.join(PROJECT_DIR, "tasks.csv")
EMAIL_SCRIPT = os.path.expanduser("~/.openclaw/workspace/skills/email-sender/scripts/send_email.py")

# ============ 颜色输出 ============
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

# ============ 数据操作 ============

def load_team():
    """加载团队配置"""
    with open(TEAM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_tasks():
    """加载所有任务"""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_tasks(tasks):
    """保存任务到 CSV"""
    if not tasks:
        return
    fieldnames = list(tasks[0].keys())
    with open(TASKS_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tasks)


def get_next_id(tasks):
    """获取下一个任务 ID"""
    if not tasks:
        return 1
    return max(int(t['id']) for t in tasks) + 1


def find_task(tasks, task_id):
    """根据 ID 查找任务"""
    for t in tasks:
        if t['id'] == str(task_id):
            return t
    return None


def find_member(team, name):
    """根据名字查找成员"""
    for m in team['members']:
        if m['name'].lower() == name.lower():
            return m
    return None


# ============ 核心功能 ============

def list_tasks(status_filter=None, member_filter=None):
    """列出任务"""
    tasks = load_tasks()
    team = load_team()
    
    if status_filter:
        tasks = [t for t in tasks if t['status'] == status_filter]
    if member_filter:
        tasks = [t for t in tasks if t['assigned_to'].lower() == member_filter.lower()]
    
    if not tasks:
        print("📭 暂无任务")
        return
    
    print(f"\n{Colors.BOLD}📋 ENT 团队任务看板{Colors.END}")
    print(f"{Colors.CYAN}项目：{team['project_name']} | 课程：{team['course']}{Colors.END}")
    print("=" * 80)
    print(f"{'ID':<4} {'任务':<20} {'负责人':<8} {'截止':<12} {'状态':<8} {'进度':<8} {'优先级'}")
    print("-" * 80)
    
    for t in tasks:
        status_color = Colors.GREEN if t['status'] == '已完成' else \
                      Colors.YELLOW if t['status'] == '进行中' else Colors.RED
        
        print(f"{t['id']:<4} {t['task_name']:<20} {t['assigned_to']:<8} "
              f"{t['deadline']:<12} {status_color}{t['status']:<6}{Colors.END} "
              f"{t['progress']:<8} {t['priority']}")
    
    print("=" * 80)
    print(f"总计 {len(tasks)} 项任务\n")


def add_task(task_name, description, assigned_to, deadline, priority="中"):
    """添加新任务"""
    tasks = load_tasks()
    team = load_team()
    
    # 检查成员是否存在
    member = find_member(team, assigned_to)
    if not member and assigned_to != "待分配":
        print(f"⚠️  警告：团队成员中未找到 '{assigned_to}'，但任务仍会被创建")
    
    new_task = {
        'id': str(get_next_id(tasks)),
        'task_name': task_name,
        'description': description,
        'assigned_to': assigned_to,
        'deadline': deadline,
        'status': '待开始',
        'progress': '0%',
        'priority': priority,
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'updated_at': datetime.now().strftime('%Y-%m-%d'),
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    print(f"\n✅ 任务已创建：#{new_task['id']} {task_name}")
    print(f"   负责人：{assigned_to} | 截止：{deadline} | 优先级：{priority}")
    
    # 如果指定了有效成员，询问是否发邮件
    if member:
        print(f"\n💡 提示：可以发送邮件通知 {member['name']} ({member['email']})")
    
    return new_task


def update_task(task_id, **kwargs):
    """更新任务"""
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 未找到任务 #{task_id}")
        return False
    
    valid_fields = ['task_name', 'description', 'assigned_to', 'deadline', 
                    'status', 'progress', 'priority']
    
    for key, value in kwargs.items():
        if key in valid_fields:
            old = task[key]
            task[key] = value
            print(f"  {key}: {old} → {value}")
    
    task['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    save_tasks(tasks)
    
    print(f"\n✅ 任务 #{task_id} 已更新")
    return True


def update_progress(task_id, progress, status=None):
    """更新任务进度"""
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 未找到任务 #{task_id}")
        return False
    
    task['progress'] = progress if '%' in progress else f"{progress}%"
    
    # 自动推断状态
    if status:
        task['status'] = status
    else:
        p = int(task['progress'].replace('%', ''))
        if p == 0:
            task['status'] = '待开始'
        elif p >= 100:
            task['status'] = '已完成'
            task['progress'] = '100%'
        else:
            task['status'] = '进行中'
    
    task['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    save_tasks(tasks)
    
    print(f"\n📊 任务 #{task_id} '{task['task_name']}' 进度更新为 {task['progress']}")
    if task['status'] == '已完成':
        print(f"🎉 恭喜！任务已完成！")
    return True


def delete_task(task_id):
    """删除任务"""
    tasks = load_tasks()
    original_len = len(tasks)
    tasks = [t for t in tasks if t['id'] != str(task_id)]
    
    if len(tasks) == original_len:
        print(f"❌ 未找到任务 #{task_id}")
        return False
    
    save_tasks(tasks)
    print(f"\n🗑️  任务 #{task_id} 已删除")
    return True


# ============ 邮件通知 ============

def send_task_email(member_name, subject, body):
    """发送邮件给团队成员"""
    team = load_team()
    member = find_member(team, member_name)
    
    if not member:
        print(f"❌ 未找到成员 '{member_name}'")
        return False
    
    email = member['email']
    
    # 构建邮件内容
    full_body = f"""你好 {member['name']}，

{body}

---
ENT 团队数字员工
{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    # 调用 email-sender skill
    cmd = f'python3 "{EMAIL_SCRIPT}" "{email}" "{subject}" "{full_body}"'
    print(f"📧 正在发送邮件给 {member_name} ({email})...")
    
    result = os.system(cmd)
    if result == 0:
        print(f"✅ 邮件发送成功！")
        return True
    else:
        print(f"❌ 邮件发送失败 (exit code: {result})")
        return False


def notify_task_assigned(task_id):
    """通知成员有新任务"""
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 未找到任务 #{task_id}")
        return False
    
    member_name = task['assigned_to']
    subject = f"[ENT团队] 新任务分配：{task['task_name']}"
    body = f"""你被分配了新任务：

🎯 任务：{task['task_name']}
📝 描述：{task['description']}
📅 截止日期：{task['deadline']}
🔥 优先级：{task['priority']}
📊 当前状态：{task['status']}

请尽快开始工作，有任何问题随时联系团队！
"""
    
    return send_task_email(member_name, subject, body)


def notify_task_reminder(task_id, message=""):
    """发送任务提醒"""
    tasks = load_tasks()
    task = find_task(tasks, task_id)
    
    if not task:
        print(f"❌ 未找到任务 #{task_id}")
        return False
    
    member_name = task['assigned_to']
    subject = f"[ENT团队] 任务提醒：{task['task_name']} ({task['progress']})"
    
    body = f"""任务进度提醒：

🎯 任务：{task['task_name']}
📊 当前进度：{task['progress']}
📅 截止日期：{task['deadline']}
📊 当前状态：{task['status']}

{message if message else '请注意任务截止日期，如有困难请及时沟通。'}
"""
    
    return send_task_email(member_name, subject, body)


# ============ 智能建议 ============

def get_next_steps():
    """生成下一步建议"""
    tasks = load_tasks()
    team = load_team()
    
    if not tasks:
        print("📭 暂无任务，建议先创建任务列表")
        return
    
    today = datetime.now().date()
    
    # 分类统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == '已完成')
    in_progress = sum(1 for t in tasks if t['status'] == '进行中')
    pending = sum(1 for t in tasks if t['status'] == '待开始')
    
    # 即将到期（3天内）
    urgent = []
    for t in tasks:
        if t['status'] != '已完成':
            try:
                deadline = datetime.strptime(t['deadline'], '%Y-%m-%d').date()
                days_left = (deadline - today).days
                if days_left <= 3 and days_left >= 0:
                    urgent.append((t, days_left))
            except:
                pass
    
    # 未分配任务
    unassigned = [t for t in tasks if t['assigned_to'] == '待分配' or not t['assigned_to']]
    
    print(f"\n{Colors.BOLD}🧭 ENT 团队下一步行动建议{Colors.END}")
    print(f"{Colors.CYAN}生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}{Colors.END}")
    print("=" * 70)
    
    # 总体进度
    progress_rate = completed / total * 100 if total > 0 else 0
    bar = "█" * int(progress_rate / 5) + "░" * (20 - int(progress_rate / 5))
    print(f"\n📊 总体进度 [{bar}] {progress_rate:.0f}%")
    print(f"   总计 {total} 项 | 已完成 {completed} | 进行中 {in_progress} | 待开始 {pending}")
    
    # 紧急任务
    if urgent:
        print(f"\n{Colors.RED}🔥 紧急任务（3天内截止）：{Colors.END}")
        for t, days in sorted(urgent, key=lambda x: x[1]):
            day_str = f"今天" if days == 0 else f"明天" if days == 1 else f"{days}天后"
            print(f"   • #{t['id']} {t['task_name']} — {t['assigned_to']} ({day_str}截止)")
    
    # 未分配
    if unassigned:
        print(f"\n{Colors.YELLOW}⚠️  未分配任务：{Colors.END}")
        for t in unassigned:
            print(f"   • #{t['id']} {t['task_name']} — 请尽快分配负责人")
    
    # 建议
    print(f"\n{Colors.GREEN}💡 建议行动：{Colors.END}")
    
    suggestions = []
    
    if pending > 0:
        suggestions.append(f"1. 启动 {pending} 个待开始任务，优先处理高优先级项")
    
    if urgent:
        suggestions.append(f"2. 紧急跟进即将到期任务，必要时调整截止日期或增派人手")
    
    if in_progress > 0:
        suggestions.append(f"3. 检查进行中任务进度，更新最新状态")
    
    if unassigned:
        suggestions.append(f"4. 分配未指派的 {len(unassigned)} 个任务给团队成员")
    
    if progress_rate < 30:
        suggestions.append(f"5. 整体进度偏慢，建议召开简短站会同步进展")
    elif progress_rate > 70:
        suggestions.append(f"5. 进度良好！可以开始准备项目演示和文档")
    
    if not suggestions:
        suggestions.append("🎉 所有任务已完成！准备最终展示吧！")
    
    for s in suggestions:
        print(f"   {s}")
    
    print("=" * 70)


def generate_weekly_summary():
    """生成周汇总"""
    tasks = load_tasks()
    team = load_team()
    
    if not tasks:
        print("📭 暂无任务")
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    completed_this_week = [t for t in tasks if t['status'] == '已完成' and t['updated_at'] >= today]
    
    summary = f"""📧 ENT 团队周任务汇总

项目：{team['project_name']}
日期：{today}

本周完成：
"""
    
    for t in completed_this_week:
        summary += f"  ✅ {t['task_name']} — {t['assigned_to']}\n"
    
    if not completed_this_week:
        summary += "  （本周暂无完成的任务）\n"
    
    summary += f"""
进行中任务：
"""
    for t in tasks:
        if t['status'] == '进行中':
            summary += f"  🔄 {t['task_name']} ({t['progress']}) — {t['assigned_to']}\n"
    
    summary += f"""
待开始任务：
"""
    for t in tasks:
        if t['status'] == '待开始':
            summary += f"  ⏳ {t['task_name']} — {t['assigned_to']}\n"
    
    summary += "\n下周重点：\n"
    summary += get_next_steps_text()
    
    return summary


def get_next_steps_text():
    """获取建议文本（供邮件使用）"""
    tasks = load_tasks()
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == '已完成')
    pending = sum(1 for t in tasks if t['status'] == '待开始')
    
    progress_rate = completed / total * 100 if total > 0 else 0
    
    lines = []
    if pending > 0:
        lines.append(f"• 启动 {pending} 个待开始任务")
    if progress_rate < 50:
        lines.append(f"• 加快进度，当前完成率 {progress_rate:.0f}%")
    lines.append(f"• 更新任务进度并同步团队成员")
    
    return "\n".join(lines) if lines else "• 所有任务推进顺利！"


# ============ CLI 入口 ============

def print_usage():
    print(f"""
{Colors.BOLD}🎯 ENT 团队任务管理系统{Colors.END}

用法:
  python3 task_manager.py list                    # 列出所有任务
  python3 task_manager.py list --status 进行中   # 按状态筛选
  python3 task_manager.py list --member Yifeng    # 按成员筛选
  
  python3 task_manager.py add "任务名" "描述" "负责人" "截止日期" [优先级]
  
  python3 task_manager.py update <id> --progress 80
  python3 task_manager.py update <id> --status 已完成
  python3 task_manager.py update <id> --assigned_to Jiayi
  
  python3 task_manager.py notify <id>             # 通知任务负责人
  python3 task_manager.py remind <id> [消息]        # 发送提醒
  
  python3 task_manager.py delete <id>             # 删除任务
  
  python3 task_manager.py next                    # 下一步建议
  python3 task_manager.py summary                 # 生成周汇总

示例:
  python3 task_manager.py add "搭建数据库" "创建SQLite数据库" "B" "2026-05-05" 高
  python3 task_manager.py update 5 --progress 100
  python3 task_manager.py notify 3
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'list':
        status = None
        member = None
        for i, arg in enumerate(sys.argv[2:], 2):
            if arg == '--status' and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
            elif arg == '--member' and i + 1 < len(sys.argv):
                member = sys.argv[i + 1]
        list_tasks(status, member)
    
    elif cmd == 'add':
        if len(sys.argv) < 6:
            print("❌ 参数不足: add <任务名> <描述> <负责人> <截止日期> [优先级]")
            sys.exit(1)
        priority = sys.argv[6] if len(sys.argv) > 6 else "中"
        add_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], priority)
    
    elif cmd == 'update':
        if len(sys.argv) < 4:
            print("❌ 参数不足: update <id> --<字段> <值>")
            sys.exit(1)
        
        task_id = sys.argv[2]
        kwargs = {}
        i = 3
        while i < len(sys.argv):
            if sys.argv[i].startswith('--'):
                key = sys.argv[i][2:]
                if i + 1 < len(sys.argv):
                    kwargs[key] = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        if not kwargs:
            print("❌ 请指定要更新的字段，如 --progress 80")
            sys.exit(1)
        
        update_task(task_id, **kwargs)
    
    elif cmd == 'progress':
        if len(sys.argv) < 4:
            print("❌ 参数不足: progress <id> <百分比> [状态]")
            sys.exit(1)
        status = sys.argv[4] if len(sys.argv) > 4 else None
        update_progress(sys.argv[2], sys.argv[3], status)
    
    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("❌ 参数不足: delete <id>")
            sys.exit(1)
        delete_task(sys.argv[2])
    
    elif cmd == 'notify':
        if len(sys.argv) < 3:
            print("❌ 参数不足: notify <id>")
            sys.exit(1)
        notify_task_assigned(sys.argv[2])
    
    elif cmd == 'remind':
        if len(sys.argv) < 3:
            print("❌ 参数不足: remind <id> [消息]")
            sys.exit(1)
        message = sys.argv[3] if len(sys.argv) > 3 else ""
        notify_task_reminder(sys.argv[2], message)
    
    elif cmd == 'next':
        get_next_steps()
    
    elif cmd == 'summary':
        summary = generate_weekly_summary()
        print(summary)
    
    else:
        print(f"❌ 未知命令: {cmd}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
