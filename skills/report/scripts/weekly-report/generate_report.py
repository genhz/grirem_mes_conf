#!/usr/bin/env python3
"""
周报生成脚本
基于总部MES项目周工作计划.docx 模板生成周报文档

用法:
    python3 generate_report.py --template "总部MES项目周工作计划.docx" --output "周报/2026-08-27 周报.docx" \
        --period "2026年8月21日 - 2026年8月27日" \
        --author "genhz" \
        --goals "1、完成开发环境搭建并输出开发环境搭建指南|2、学习了解当前项目框架结构|3、输出数据库设计文档和后端文档" \
        --tasks "1|开发环境搭建|完成本地开发环境全套安装、调试，输出开发环境搭建指南|genhz|本周内|已完成" \
        --tasks "2|项目框架学习|学习了解当前项目框架结构，便于迅速参与开发工作|genhz|本周内|已完成"

依赖:
    pip3 install python-docx
"""

import argparse
import sys
import os
from docx import Document


def parse_args():
    parser = argparse.ArgumentParser(description="基于模板生成周报 Word 文档")
    parser.add_argument("--template", "-t", default="总部MES项目周工作计划.docx",
                        help="模板文件路径 (默认: 总部MES项目周工作计划.docx)")
    parser.add_argument("--output", "-o", default="周报/周报.docx",
                        help="输出文件路径 (默认: 周报/周报.docx)")
    parser.add_argument("--period", "-p", required=True,
                        help="统计周期，如: 2026年8月21日 - 2026年8月27日")
    parser.add_argument("--author", "-a", default="",
                        help="填报人姓名")
    parser.add_argument("--goals", "-g", default="",
                        help="本周核心目标，用 | 分隔，如: 目标1|目标2|目标3")
    parser.add_argument("--tasks", "-T", action="append", default=[],
                        help="工作明细，格式: 序号|工作模块|具体内容|负责人|完成时间|进度状态，可多次使用")
    parser.add_argument("--problems", "-P", action="append", default=[],
                        help="问题汇总，格式: 问题描述|问题原因|解决措施|完成时限|状态，可多次使用")
    parser.add_argument("--summary-done", "-d", default="",
                        help="已完成工作成果")
    parser.add_argument("--summary-undone", "-u", default="",
                        help="未完成工作及延期原因")
    parser.add_argument("--summary-suggest", "-s", default="",
                        help="优化建议")
    parser.add_argument("--next-week", "-n", action="append", default=[],
                        help="下周计划，用 | 分隔多条")
    parser.add_argument("--coordination", "-c", action="append", default=[],
                        help="需协调资源，用 | 分隔多条")
    return parser.parse_args()


def update_text(para, new_text):
    """更新段落文本，保留格式"""
    para.clear()
    run = para.add_run(new_text)
    return run


def generate_report(args):
    """生成周报文档"""
    if not os.path.exists(args.template):
        print(f"错误: 模板文件不存在: {args.template}")
        sys.exit(1)

    doc = Document(args.template)

    # 1. 更新统计周期
    for para in doc.paragraphs:
        text = para.text
        if "统计周期" in text and "年" in text and "月" in text:
            # 提取 "统计周期：" 前缀
            if "：" in text:
                prefix = text.split("：")[0] + "："
                update_text(para, f"{prefix}{args.period}")
            break

    # 2. 更新填报人
    for para in doc.paragraphs:
        if "填报人" in para.text and "：" in para.text:
            if args.author:
                prefix = para.text.split("：")[0] + "："
                update_text(para, f"{prefix}{args.author}")
            break

    # 3. 更新本周核心目标
    if args.goals:
        goal_list = args.goals.split("|")
        goal_idx = 0
        for para in doc.paragraphs:
            text = para.text
            if text.startswith("1、") or text.startswith("2、") or text.startswith("3、"):
                # 检查是否是核心目标区域（在"本周核心目标"之后）
                if goal_idx < len(goal_list):
                    # 去掉原有的 "1、" 前缀，加上新的
                    num = text[0]  # "1", "2", "3"
                    update_text(para, f"{num}、{goal_list[goal_idx].lstrip('123456789、')}")
                    goal_idx += 1
                if goal_idx >= 3:
                    break

    # 4. 更新工作明细表格
    if args.tasks:
        for table in doc.tables:
            for row_idx, row in enumerate(table.rows):
                cells = row.cells
                if len(cells) < 6:
                    continue

                if row_idx < len(args.tasks):
                    task = args.tasks[row_idx].split("|")
                    if len(task) >= 6:
                        cells[0].text = task[0]  # 序号
                        cells[1].text = task[1]  # 工作模块
                        cells[2].text = task[2]  # 具体内容
                        if len(task) > 3:
                            cells[3].text = task[3]  # 负责人
                        if len(task) > 4:
                            cells[4].text = task[4]  # 完成时间
                        if len(task) > 5:
                            cells[5].text = task[5]  # 进度状态
                else:
                    # 清空多余行
                    cells[0].text = ""
                    cells[1].text = ""
                    cells[2].text = ""
                    cells[5].text = ""

    # 5. 更新问题汇总
    if args.problems:
        # 问题汇总通常在表格中
        for table in doc.tables:
            for row_idx, row in enumerate(table.rows):
                cells = row.cells
                if len(cells) < 5:
                    continue
                # 跳过表头行
                if "问题描述" in cells[0].text or "问题" in cells[0].text:
                    continue
                if row_idx - 1 < len(args.problems):
                    prob = args.problems[row_idx - 1].split("|")
                    if len(prob) >= 5:
                        cells[0].text = prob[0]
                        cells[1].text = prob[1]
                        cells[2].text = prob[2]
                        cells[3].text = prob[3]
                        cells[4].text = prob[4]
                break

    # 6. 更新复盘总结
    for para in doc.paragraphs:
        text = para.text
        if "1、已完成工作成果：" in text and args.summary_done:
            update_text(para, f"1、已完成工作成果：{args.summary_done}")
        elif "2、未完成工作及延期原因：" in text and args.summary_undone:
            update_text(para, f"2、未完成工作及延期原因：{args.summary_undone}")
        elif "3、优化建议：" in text and args.summary_suggest:
            update_text(para, f"3、优化建议：{args.summary_suggest}")

    # 7. 更新下周计划
    if args.next_week:
        plan_idx = 0
        for para in doc.paragraphs:
            text = para.text
            if text.startswith("1、") or text.startswith("2、") or text.startswith("3、") or text.startswith("4、"):
                # 检查是否是下周计划区域
                if plan_idx < len(args.next_week):
                    num = text[0]
                    update_text(para, f"{num}、{args.next_week[plan_idx].lstrip('123456789、')}")
                    plan_idx += 1
                if plan_idx >= 4:
                    break

    # 8. 更新需协调资源
    if args.coordination:
        coord_idx = 0
        for para in doc.paragraphs:
            text = para.text
            if text.startswith("1、") or text.startswith("2、"):
                # 检查是否是需要协调资源区域
                if coord_idx < len(args.coordination):
                    num = text[0]
                    update_text(para, f"{num}、{args.coordination[coord_idx].lstrip('123456789、')}")
                    coord_idx += 1
                if coord_idx >= 2:
                    break

    # 保存文档
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc.save(args.output)
    print(f"周报生成成功: {args.output}")


if __name__ == "__main__":
    args = parse_args()
    generate_report(args)
