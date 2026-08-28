#!/usr/bin/env python3
"""
快速周报生成脚本 - 基于模板生成周报

用法:
    python3 quick_report.py

交互模式: 按提示输入周报内容
直接模式: 通过命令行参数指定

依赖: pip3 install python-docx
"""

import sys
import os
from docx import Document


def create_report(template_path, output_path, data):
    """
    基于模板生成周报

    Args:
        template_path: 模板文件路径
        output_path: 输出文件路径
        data: 周报数据字典
            {
                "period": "2026年8月21日 - 2026年8月27日",
                "author": "genhz",
                "goals": ["目标1", "目标2", "目标3"],
                "tasks": [
                    {"num": "1", "module": "开发环境搭建", "content": "完成...", "owner": "genhz", "time": "本周内", "status": "已完成"}
                ],
                "problems": [
                    {"desc": "...", "reason": "...", "solution": "...", "time": "...", "status": "..."}
                ],
                "summary_done": "已完成...",
                "summary_undone": "未完成...",
                "summary_suggest": "优化建议...",
                "next_week": ["计划1", "计划2", "计划3", "计划4"],
                "coordination": ["需要协调...", "无其他..."]
            }
    """
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在: {template_path}")
        return False

    doc = Document(template_path)

    # 更新段落内容
    in_core_goals = False
    in_next_week = False
    in_coordination = False
    goal_count = 0
    next_count = 0
    coord_count = 0

    for para in doc.paragraphs:
        text = para.text

        # 统计周期
        if "统计周期" in text and "年" in text and "月" in text and "：" in text:
            prefix = text.split("：")[0] + "："
            _clear_and_write(para, f"{prefix}{data.get('period', '')}")

        # 填报人
        elif "填报人" in text and "：" in text:
            prefix = text.split("：")[0] + "："
            _clear_and_write(para, f"{prefix}{data.get('author', '')}")

        # 本周核心目标
        elif "本周核心目标" in text:
            in_core_goals = True
            goal_count = 0
            in_next_week = False
            in_coordination = False

        elif in_core_goals and goal_count < len(data.get("goals", [])):
            num = text[0] if text and text[0].isdigit() else str(goal_count + 1)
            goal = data["goals"][goal_count]
            _clear_and_write(para, f"{num}、{goal}")
            goal_count += 1
            if goal_count >= 3:
                in_core_goals = False

        # 已完成工作成果
        elif "1、已完成工作成果：" in text:
            if data.get("summary_done"):
                _clear_and_write(para, f"1、已完成工作成果：{data['summary_done']}")

        # 未完成工作
        elif "2、未完成工作及延期原因：" in text:
            if data.get("summary_undone"):
                _clear_and_write(para, f"2、未完成工作及延期原因：{data['summary_undone']}")

        # 优化建议
        elif "3、优化建议：" in text:
            if data.get("summary_suggest"):
                _clear_and_write(para, f"3、优化建议：{data['summary_suggest']}")

        # 下周重点工作计划
        elif "下周重点工作计划" in text or ("下周" in text and "计划" in text):
            in_next_week = True
            next_count = 0
            in_coordination = False

        elif in_next_week and next_count < len(data.get("next_week", [])):
            num = text[0] if text and text[0].isdigit() else str(next_count + 1)
            plan = data["next_week"][next_count]
            _clear_and_write(para, f"{num}、{plan}")
            next_count += 1
            if next_count >= 4:
                in_next_week = False

        # 需协调资源
        elif "协调" in text and ("资源" in text or "支持" in text):
            in_coordination = True
            coord_count = 0

        elif in_coordination and coord_count < len(data.get("coordination", [])):
            num = text[0] if text and text[0].isdigit() else str(coord_count + 1)
            coord = data["coordination"][coord_count]
            _clear_and_write(para, f"{num}、{coord}")
            coord_count += 1
            if coord_count >= 2:
                in_coordination = False

    # 更新表格
    for table in doc.tables:
        for row_idx, row in enumerate(table.rows):
            cells = row.cells
            if len(cells) < 5:
                continue

            # 工作明细表格 (6列)
            if len(cells) >= 6 and data.get("tasks"):
                if row_idx < len(data["tasks"]):
                    task = data["tasks"][row_idx]
                    cells[0].text = task.get("num", "")
                    cells[1].text = task.get("module", "")
                    cells[2].text = task.get("content", "")
                    cells[3].text = task.get("owner", "")
                    cells[4].text = task.get("time", "")
                    cells[5].text = task.get("status", "")
                else:
                    # 清空多余行
                    for i in range(len(cells)):
                        cells[i].text = ""

            # 问题汇总表格 (5列)
            elif len(cells) == 5 and data.get("problems"):
                if "问题描述" in cells[0].text or "问题" in cells[0].text:
                    continue  # 跳过表头
                if row_idx - 1 < len(data["problems"]):
                    prob = data["problems"][row_idx - 1]
                    cells[0].text = prob.get("desc", "")
                    cells[1].text = prob.get("reason", "")
                    cells[2].text = prob.get("solution", "")
                    cells[3].text = prob.get("time", "")
                    cells[4].text = prob.get("status", "")

    # 保存
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc.save(output_path)
    print(f"周报生成成功: {output_path}")
    return True


def _clear_and_write(para, text):
    """清空段落并写入新文本"""
    para.clear()
    para.add_run(text)


def interactive_mode():
    """交互模式 - 引导用户输入周报内容"""
    print("=" * 50)
    print("周报生成工具")
    print("=" * 50)

    template = input(f"模板文件路径 (默认: 总部MES项目周工作计划.docx): ").strip()
    if not template:
        template = "总部MES项目周工作计划.docx"

    output = input(f"输出文件路径 (默认: 周报/周报.docx): ").strip()
    if not output:
        output = "周报/周报.docx"

    period = input("统计周期 (如: 2026年8月21日 - 2026年8月27日): ").strip()
    author = input("填报人: ").strip()

    print("\n本周核心目标 (输入3条，直接回车跳过):")
    goals = []
    for i in range(1, 4):
        g = input(f"  目标{i}: ").strip()
        if g:
            goals.append(g)

    print("\n工作明细 (输入任务，直接回车跳过):")
    tasks = []
    while True:
        num = input(f"  任务序号 (或回车结束): ").strip()
        if not num:
            break
        module = input(f"  工作模块: ").strip()
        content = input(f"  具体内容: ").strip()
        owner = input(f"  负责人: ").strip()
        time = input(f"  完成时间: ").strip()
        status = input(f"  进度状态: ").strip()
        tasks.append({
            "num": num, "module": module, "content": content,
            "owner": owner, "time": time, "status": status
        })

    summary_done = input("\n已完成工作成果: ").strip()
    summary_undone = input("未完成工作及延期原因: ").strip()
    summary_suggest = input("优化建议: ").strip()

    print("\n下周计划 (输入4条，直接回车跳过):")
    next_week = []
    for i in range(1, 5):
        p = input(f"  计划{i}: ").strip()
        if p:
            next_week.append(p)

    print("\n需协调资源 (输入2条，直接回车跳过):")
    coordination = []
    for i in range(1, 3):
        c = input(f"  事项{i}: ").strip()
        if c:
            coordination.append(c)

    data = {
        "period": period,
        "author": author,
        "goals": goals,
        "tasks": tasks,
        "summary_done": summary_done,
        "summary_undone": summary_undone,
        "summary_suggest": summary_suggest,
        "next_week": next_week,
        "coordination": coordination,
    }

    create_report(template, output, data)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 交互模式
        interactive_mode()
    else:
        print("请使用交互模式运行: python3 quick_report.py")
        print("或参考 generate_report.py 使用命令行参数模式")
