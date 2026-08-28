# 周报生成脚本

> 基于 Word 模板快速生成周报文档

---

## 环境准备

```bash
pip3 install -r requirements.txt
# 或
pip3 install python-docx
```

---

## 使用方式

### 方式一：交互模式（推荐）

```bash
python3 quick_report.py
```

按提示依次输入：
- 统计周期
- 填报人
- 本周核心目标（3 条）
- 工作明细
- 复盘总结
- 下周计划
- 需协调资源

### 方式二：命令行参数模式

```bash
python3 generate_report.py \
    -t "总部MES项目周工作计划.docx" \
    -o "周报/2026-08-27 周报.docx" \
    -p "2026 年 8 月 21 日 - 2026 年 8 月 27 日" \
    -a "genhz" \
    -g "目标 1|目标 2|目标 3" \
    -T "1|模块名|具体内容|负责人|时间|状态"
```

---

## 参数说明

| 参数 | 简写 | 说明 |
|------|------|------|
| `--template` | `-t` | 模板文件路径 |
| `--output` | `-o` | 输出文件路径 |
| `--period` | `-p` | 统计周期 |
| `--author` | `-a` | 填报人 |
| `--goals` | `-g` | 本周核心目标（\| 分隔） |
| `--tasks` | `-T` | 工作明细（可多次使用） |
| `--summary-done` | `-d` | 已完成工作成果 |
| `--summary-undone` | `-u` | 未完成工作及延期原因 |
| `--summary-suggest` | `-s` | 优化建议 |
| `--next-week` | `-n` | 下周计划（可多次使用） |
| `--coordination` | `-c` | 需协调资源（可多次使用） |

---

## 注意事项

1. 确保模板文件 `总部MES项目周工作计划.docx` 在项目根目录
2. 周报统一输出到 `周报/` 目录
3. 文件命名格式：`YYYY-MM-DD 周报.docx`
4. Python 版本需要 3.8+
