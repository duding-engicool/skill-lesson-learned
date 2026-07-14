#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经验教训（LL）知识库报告生成器
读入结构化结果 JSON，生成纯文字版 .txt + Markdown .md（双文件、无网页版）。

用法：
  python build_report.py --input result.json --out-dir ./out
  python build_report.py --out-dir ./out          # 使用内置小样本

输入 JSON 结构：
{
  "title":"经验教训知识库（2026）",
  "owner":"知识库管理员",
  "lessons":[
    {
      "id":"LL-2026-001",
      "source":"项目A 试产阶段",
      "date":"2026-03-12",
      "background":"项目A 试产，SMT 线",
      "phenomenon":"首件合格率偏低，虚焊",
      "category":"工艺制造",
      "nature":"负面教训",
      "severity":"高",
      "root_cause":"钢网开口设计不合理 + 回流焊温度曲线偏移",
      "corrective":"调整钢网开口，重设炉温曲线",
      "preventive":"将炉温曲线纳入 PFMEA 与首件检查清单",
      "owner":"待企业补充",
      "status":"关闭",
      "tags":["SMT","虚焊","炉温曲线"]
    }
  ]
}
索引（按类别/标签）由脚本自动从 lessons 生成。
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date

NATURE_LABEL = {
    "正面经验": "正面经验",
    "负面教训": "负面教训",
}


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_index(lessons):
    by_cat = defaultdict(list)
    by_tag = defaultdict(list)
    for L in lessons:
        by_cat[L.get("category", "待企业补充")].append(L.get("id", ""))
        for t in L.get("tags", []) or []:
            by_tag[t].append(L.get("id", ""))
    return by_cat, by_tag


def field(L, k):
    v = L.get(k, "")
    return v if v not in (None, "", []) else "待企业补充"


def build_md(r):
    lessons = r.get("lessons", []) or []
    by_cat, by_tag = build_index(lessons)
    out = []
    out.append(f"# {r.get('title','经验教训知识库')}\n")
    out.append("## 一、概览\n")
    out.append(f"- 知识库负责人：{r.get('owner','') or '待企业补充'}")
    out.append(f"- 条目总数：{len(lessons)}")
    out.append("")
    out.append("## 二、知识库索引\n")
    out.append("### 按类别\n")
    for cat, ids in by_cat.items():
        out.append(f"- {cat}：{', '.join(ids)}")
    out.append("")
    out.append("### 按标签\n")
    for tag, ids in by_tag.items():
        out.append(f"- {tag}：{', '.join(ids)}")
    out.append("")
    out.append("## 三、经验教训条目\n")
    for L in lessons:
        out.append(f"### {field(L,'id')} 〔{field(L,'nature')}〕\n")
        out.append(f"- 来源：{field(L,'source')} ｜ 日期：{field(L,'date')}")
        out.append(f"- 类别：{field(L,'category')} ｜ 严重度：{field(L,'severity')} ｜ 状态：{field(L,'status')}")
        out.append(f"- 背景：{field(L,'background')}")
        out.append(f"- 现象：{field(L,'phenomenon')}")
        out.append(f"- 根因：{field(L,'root_cause')}")
        out.append(f"- 纠正措施：{field(L,'corrective')}")
        out.append(f"- 预防措施：{field(L,'preventive')}")
        tags = field(L, 'tags')
        tags_s = ', '.join(tags) if isinstance(tags, list) else tags
        out.append(f"- 责任人：{field(L,'owner')} ｜ 标签：{tags_s}")
        out.append("")
    out.append(f"> 报告生成时间：{date.today().strftime('%Y-%m-%d')} ｜ 输出：纯文字版(.txt) + Markdown(.md)")
    return "\n".join(out)


def build_txt(r):
    lessons = r.get("lessons", []) or []
    by_cat, by_tag = build_index(lessons)
    L = []
    L.append("=" * 72)
    L.append(f"经验教训知识库 · {r.get('title','经验教训知识库')}")
    L.append("=" * 72)
    L.append("")
    L.append(f"知识库负责人：{r.get('owner','') or '待企业补充'}")
    L.append(f"条目总数    ：{len(lessons)}")
    L.append("")

    # 一、知识库索引
    L.append("-" * 72)
    L.append("一、知识库索引")
    L.append("-" * 72)
    L.append("  按类别：")
    for cat, ids in by_cat.items():
        L.append(f"    {cat}：{', '.join(ids)}")
    L.append("  按标签：")
    for tag, ids in by_tag.items():
        L.append(f"    {tag}：{', '.join(ids)}")
    L.append("")

    # 二、经验教训条目
    L.append("-" * 72)
    L.append("二、经验教训条目")
    L.append("-" * 72)
    for item in lessons:
        L.append(f"  {field(item,'id')} 〔{field(item,'nature')}〕")
        L.append(f"    来源    ：{field(item,'source')} ｜ 日期：{field(item,'date')}")
        L.append(f"    类别    ：{field(item,'category')} ｜ 严重度：{field(item,'severity')} ｜ 状态：{field(item,'status')}")
        L.append(f"    背景    ：{field(item,'background')}")
        L.append(f"    现象    ：{field(item,'phenomenon')}")
        L.append(f"    根因    ：{field(item,'root_cause')}")
        L.append(f"    纠正措施：{field(item,'corrective')}")
        L.append(f"    预防措施：{field(item,'preventive')}")
        tags = field(item, 'tags')
        tags_s = ', '.join(tags) if isinstance(tags, list) else tags
        L.append(f"    责任人  ：{field(item,'owner')} ｜ 标签：{tags_s}")
        L.append("")

    L.append("-" * 72)
    L.append(f"报告生成时间：{date.today().strftime('%Y-%m-%d')} ｜ 输出：纯文字版(.txt) + Markdown(.md)")
    L.append("")
    return "\n".join(L)


SAMPLE = {
    "title": "经验教训知识库（2026，演示样本）",
    "owner": "待企业补充",
    "lessons": [
        {
            "id": "LL-2026-001", "source": "项目A 试产阶段", "date": "2026-03-12",
            "background": "项目A 试产，SMT 生产线", "phenomenon": "首件合格率偏低，存在虚焊",
            "category": "工艺制造", "nature": "负面教训", "severity": "高",
            "root_cause": "钢网开口设计不合理 + 回流焊温度曲线偏移",
            "corrective": "调整钢网开口，重设炉温曲线并验证",
            "preventive": "将炉温曲线纳入 PFMEA 与首件检查清单",
            "owner": "待企业补充", "status": "关闭",
            "tags": ["SMT", "虚焊", "炉温曲线"]
        },
        {
            "id": "LL-2026-002", "source": "供应商导入审核", "date": "2026-04-20",
            "background": "新供应商 B 准入审核", "phenomenon": "PPAP 提交延迟且资料不全",
            "category": "供应链", "nature": "负面教训", "severity": "中",
            "root_cause": "未提前明确 PPAP 等级与提交清单",
            "corrective": "补发 PPAP 并按等级重审",
            "preventive": "在定点协议中固化 PPAP 等级与节点",
            "owner": "待企业补充", "status": "待验证",
            "tags": ["PPAP", "供应商导入"]
        },
        {
            "id": "LL-2026-003", "source": "项目C 量产爬坡", "date": "2026-05-30",
            "background": "项目C 量产爬坡", "phenomenon": "通过分层审核显著减少装配漏装",
            "category": "项目管理", "nature": "正面经验", "severity": "低",
            "root_cause": "（正面经验，无根因）",
            "corrective": "（正面经验）",
            "preventive": "将分层审核(LPA)推广至其他产线",
            "owner": "待企业补充", "status": "开放",
            "tags": ["LPA", "分层审核", "防错"]
        }
    ]
}


def main():
    ap = argparse.ArgumentParser(description="经验教训知识库报告生成器（txt + md）")
    ap.add_argument("--input", help="结构化结果 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all",
                    help="输出格式：txt / md / all（默认 all = txt + md）")
    args = ap.parse_args()

    if args.input:
        try:
            r = load_result(args.input)
        except Exception as e:
            sys.stderr.write(f"读取输入失败：{e}\n")
            sys.exit(1)
    else:
        r = SAMPLE
        print("ℹ️ 未提供 --input，使用内置小样本数据。")

    title = str(r.get("title", "经验教训知识库")).replace("/", "-")
    date_str = date.today().strftime("%Y%m%d")
    base = f"经验教训库_{title}_{date_str}"
    os.makedirs(args.out_dir, exist_ok=True)

    if args.format in ("md", "all"):
        md = build_md(r)
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ MD : {md_path}")

    if args.format in ("txt", "all"):
        txt = build_txt(r)
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"✅ TXT: {txt_path}")

    print(f"   条目数：{len(r.get('lessons', []) or [])}")


if __name__ == "__main__":
    main()
