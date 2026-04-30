# 🌸 植物湿度监测 Skill — 小红花

实时查询 SQLite 数据库中的湿度数据，并以大圣风格回复用户。

## 文件结构

```
plant-humidity/
  SKILL.md
  scripts/
    check.py        # 主查询脚本
  resources/
    plant-care.md   # 植物湿度参考知识
```

## 使用方法

当用户询问植物/小红花湿度时，用 exec 调用：

```bash
# 中文回复（默认）
python3 ~/.openclaw/workspace/skills/plant-humidity/scripts/check.py

# 英文回复
python3 ~/.openclaw/workspace/skills/plant-humidity/scripts/check.py --en
```

或者指定数据库路径：

```bash
python3 ~/.openclaw/workspace/skills/plant-humidity/scripts/check.py /path/to/humidity.db
```

脚本自动读取默认数据库路径：
`/mnt/c/Users/chunyi/Desktop/code/code/humidity.db`

## 正常湿度参考

- **< 30%** 🔴 过干 — 土壤都快裂了，快浇水！
- **30-50%** 🟡 偏干 — 有点口渴，建议补水
- **50-70%** 🟢 良好 — 舒适区，小红花很开心
- **70-90%** 🟡 偏湿 — 有点潮，注意通风
- **> 90%** 🔴 过湿 — 容易烂根，别浇了！

## 大圣回复风格

每次回复要：
1. 直接报数字
2. 给一个状态判断
3. 带点小幽默/俏皮话
4. 必要时给建议
