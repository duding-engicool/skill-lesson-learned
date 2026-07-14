#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经验教训（LL）知识库报告生成器
读入结构化结果 JSON，生成 MD 文档 + 网页版 HTML（双版）。主色 #C8102E。

用法：
  python build_report.py --input result.json --md-out report.md --html-out report.html
  python build_report.py --demo            # 使用内置小样本

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
import sys
import html
from datetime import datetime
from collections import defaultdict

PRIMARY = "#C8102E"

NATURE_COLOR = {
    "正面经验": "#16a34a",
    "负面教训": "#C8102E",
}
SEVERITY_COLOR = {
    "高": "#C8102E",
    "中": "#ea580c",
    "低": "#2563eb",
}


def esc(s):
    return html.escape(str(s), quote=True)


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
        out.append(f"### {L.get('id','')} 〔{L.get('nature','')}〕\n")
        out.append(f"- 来源：{L.get('source','待企业补充')} ｜ 日期：{L.get('date','待企业补充')}")
        out.append(f"- 类别：{L.get('category','待企业补充')} ｜ 严重度：{L.get('severity','待企业补充')} ｜ 状态：{L.get('status','待企业补充')}")
        out.append(f"- 背景：{L.get('background','待企业补充')}")
        out.append(f"- 现象：{L.get('phenomenon','待企业补充')}")
        out.append(f"- 根因：{L.get('root_cause','待企业补充')}")
        out.append(f"- 纠正措施：{L.get('corrective','待企业补充')}")
        out.append(f"- 预防措施：{L.get('preventive','待企业补充')}")
        out.append(f"- 责任人：{L.get('owner','待企业补充')} ｜ 标签：{', '.join(L.get('tags',[]) or []) or '待企业补充'}")
        out.append("")
    out.append(f"> 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 主色 {PRIMARY}")
    return "\n".join(out)


CSS = """
:root{--primary:#C8102E;--bg:#f8fafc;--card:#ffffff;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.7;padding:32px}
.wrap{max-width:1080px;margin:0 auto}
header{text-align:center;padding:28px 0 18px;border-bottom:3px solid var(--primary);margin-bottom:28px}
header h1{font-size:26px;letter-spacing:1px;color:var(--primary)}
header .meta{color:var(--muted);font-size:14px;margin-top:10px}
.sec{background:var(--card);border-radius:14px;padding:24px;box-shadow:0 4px 16px rgba(0,0,0,.06);margin-bottom:28px}
.sec h2{font-size:21px;margin-bottom:16px;border-left:5px solid var(--primary);padding-left:12px}
.lcard{border:1px solid var(--line);border-left:5px solid var(--primary);border-radius:10px;padding:16px;margin-bottom:16px}
.lcard h3{font-size:17px;margin-bottom:8px}
.kv{font-size:14px;margin:4px 0}
.badge{display:inline-block;color:#fff;border-radius:6px;padding:1px 8px;font-size:12px;font-weight:700;margin-right:6px}
.idx{font-size:14px;line-height:2}
.tag{display:inline-block;background:#fef2f2;color:var(--primary);border-radius:14px;padding:2px 10px;font-size:12px;margin:2px}
footer{text-align:center;color:var(--muted);font-size:12px;margin-top:20px}
"""


def build_html(r):
    lessons = r.get("lessons", []) or []
    by_cat, by_tag = build_index(lessons)

    cards = []
    for L in lessons:
        nat = L.get("nature", "待企业补充")
        nat_color = NATURE_COLOR.get(nat, "#64748b")
        sev = L.get("severity", "待企业补充")
        sev_color = SEVERITY_COLOR.get(sev, "#64748b")
        tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in L.get("tags", []) or [])
        cards.append(
            f'<div class="lcard"><h3>{esc(L.get("id",""))} '
            f'<span class="badge" style="background:{nat_color}">{esc(nat)}</span>'
            f'<span class="badge" style="background:{sev_color}">严重度 {esc(sev)}</span></h3>'
            f'<div class="kv"><b>来源：</b>{esc(L.get("source","待企业补充"))} ｜ <b>日期：</b>{esc(L.get("date","待企业补充"))}'
            f' ｜ <b>类别：</b>{esc(L.get("category","待企业补充"))} ｜ <b>状态：</b>{esc(L.get("status","待企业补充"))}</div>'
            f'<div class="kv"><b>背景：</b>{esc(L.get("background","待企业补充"))}</div>'
            f'<div class="kv"><b>现象：</b>{esc(L.get("phenomenon","待企业补充"))}</div>'
            f'<div class="kv"><b>根因：</b>{esc(L.get("root_cause","待企业补充"))}</div>'
            f'<div class="kv"><b>纠正：</b>{esc(L.get("corrective","待企业补充"))}</div>'
            f'<div class="kv"><b>预防：</b>{esc(L.get("preventive","待企业补充"))}</div>'
            f'<div class="kv"><b>责任人：</b>{esc(L.get("owner","待企业补充"))}</div>'
            f'<div class="kv"><b>标签：</b>{tags or "待企业补充"}</div></div>'
        )
    cards_html = "".join(cards) if cards else '<p style="color:#64748b">（暂无 LL 条目，待企业补充）</p>'

    cat_html = "".join(f'<span class="tag">{esc(c)}：{esc(", ".join(ids))}</span>' for c, ids in by_cat.items()) or "（暂无）"
    tag_html = "".join(f'<span class="tag">{esc(t)}：{esc(", ".join(ids))}</span>' for t, ids in by_tag.items()) or "（暂无）"

    return (
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{esc(r.get('title','经验教训知识库'))}</title>"
        f"<style>{CSS}</style></head><body><div class='wrap'>"
        f"<header><h1>{esc(r.get('title','经验教训知识库'))}</h1>"
        f"<div class='meta'>负责人：{esc(r.get('owner','') or '待企业补充')} ｜ 条目数：{len(lessons)}</div></header>"
        "<section class='sec'><h2>知识库索引</h2>"
        f"<div class='idx'><b>按类别：</b><br>{cat_html}<br><br><b>按标签：</b><br>{tag_html}</div></section>"
        "<section class='sec'><h2>经验教训条目</h2>" + cards_html + "</section>"
        f"<footer>本报告由 经验教训（LL）结构化沉淀 生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 主色 {PRIMARY}</footer>"
        "</div></body></html>"
    )


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
    ap = argparse.ArgumentParser(description="经验教训知识库报告生成器")
    ap.add_argument("--input", help="结构化结果 JSON 路径")
    ap.add_argument("--md-out", default="demo_ll.md", help="输出 MD 路径")
    ap.add_argument("--html-out", default="demo_ll.html", help="输出 HTML 路径")
    ap.add_argument("--demo", action="store_true", help="使用内置小样本生成演示报告")
    args = ap.parse_args()

    if args.demo:
        r = SAMPLE
    elif args.input:
        try:
            r = load_result(args.input)
        except Exception as e:
            sys.stderr.write(f"读取输入失败：{e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("请使用 --input <json> 或 --demo。\n")
        sys.exit(1)

    with open(args.md_out, "w", encoding="utf-8") as f:
        f.write(build_md(r))
    sys.stderr.write(f"MD 已生成：{args.md_out}\n")
    with open(args.html_out, "w", encoding="utf-8") as f:
        f.write(build_html(r))
    sys.stderr.write(f"HTML 已生成：{args.html_out}\n")


if __name__ == "__main__":
    main()
