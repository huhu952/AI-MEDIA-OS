#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-MEDIA-OS 内容实验数据库管理脚本（仅依赖标准库）

子命令：
  init                    创建 database/content_experiments.sqlite（按 database/schema.sql）
  add <json>              新增 / 覆盖一条记录（JSON 字符串或 JSON 文件路径）
  import <csv>            从 CSV 导入（表头须与模板一致）
  export [--out FILE]     导出 CSV（默认输出到 stdout）
  list                    列出全部记录（摘要字段）
  stats                   基础统计（按平台）

示例：
  python scripts/content_db.py init
  python scripts/content_db.py add "{\"content_id\":\"P001-20260816\",\"platform\":\"douyin\",\"topic\":\"测试\"}"
  python scripts/content_db.py import database/content_experiments_template.csv
  python scripts/content_db.py export --out database/content_experiments_backup.csv
"""

import argparse
import csv
import json
import os
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(BASE, "database", "content_experiments.sqlite")
SCHEMA = os.path.join(BASE, "database", "schema.sql")

FIELDS = [
    "content_id", "platform", "publish_date", "series", "topic", "content_type",
    "duration", "hook_type", "visual_style", "characters", "generation_models",
    "image_generation_count", "video_generation_count", "failed_generation_count",
    "estimated_image_cost", "estimated_video_cost", "estimated_audio_cost",
    "total_cost", "production_time", "views", "likes", "comments", "shares",
    "favorites", "followers_gained", "three_second_retention", "completion_rate",
    "revenue", "notes",
]

INT_FIELDS = {
    "image_generation_count", "video_generation_count", "failed_generation_count",
    "views", "likes", "comments", "shares", "favorites", "followers_gained",
}
FLOAT_FIELDS = {
    "duration", "estimated_image_cost", "estimated_video_cost", "estimated_audio_cost",
    "total_cost", "production_time", "three_second_retention", "completion_rate",
    "revenue",
}


def connect(db):
    return sqlite3.connect(db)


def clean(row):
    out = {}
    for k in FIELDS:
        v = row.get(k, "")
        if v is None or (isinstance(v, str) and v.strip() == ""):
            out[k] = None
        elif k in INT_FIELDS:
            out[k] = int(float(v))
        elif k in FLOAT_FIELDS:
            out[k] = float(v)
        else:
            out[k] = str(v).strip()
    return out


def upsert(con, row):
    c = clean(row)
    if not c.get("content_id"):
        raise ValueError("content_id 必填")
    cols = [k for k in FIELDS if k != "content_id"]
    updates = ", ".join(f"{k}=excluded.{k}" for k in cols) + ", updated_at=datetime('now','localtime')"
    con.execute(
        f"INSERT INTO content_experiments ({','.join(FIELDS)}) VALUES ({','.join('?' * len(FIELDS))}) "
        f"ON CONFLICT(content_id) DO UPDATE SET {updates}",
        [c[k] for k in FIELDS],
    )


def cmd_init(args):
    with open(SCHEMA, encoding="utf-8") as f:
        sql = f.read()
    con = connect(args.db)
    con.executescript(sql)
    con.commit()
    con.close()
    print(f"[init] ok: {args.db}")


def cmd_add(args):
    payload = args.json
    if os.path.exists(payload):
        with open(payload, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.loads(payload)
    con = connect(args.db)
    upsert(con, data)
    con.commit()
    con.close()
    print(f"[add] ok: {data.get('content_id')}")


def cmd_import(args):
    con = connect(args.db)
    n = 0
    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            upsert(con, row)
            n += 1
    con.commit()
    con.close()
    print(f"[import] ok: {n} rows from {args.csv}")


def cmd_export(args):
    con = connect(args.db)
    rows = con.execute(
        f"SELECT {','.join(FIELDS)} FROM content_experiments ORDER BY publish_date, content_id"
    ).fetchall()
    con.close()
    if args.out:
        with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(FIELDS)
            w.writerows(rows)
        print(f"[export] ok: {len(rows)} rows -> {args.out}")
    else:
        w = csv.writer(sys.stdout)
        w.writerow(FIELDS)
        w.writerows(rows)


def cmd_list(args):
    con = connect(args.db)
    rows = con.execute(
        "SELECT content_id, platform, publish_date, topic, views, likes, total_cost "
        "FROM content_experiments ORDER BY publish_date, content_id"
    ).fetchall()
    con.close()
    for r in rows:
        print(" | ".join("" if x is None else str(x) for x in r))
    print(f"[list] total: {len(rows)}")


def cmd_stats(args):
    con = connect(args.db)
    total = con.execute("SELECT COUNT(*) FROM content_experiments").fetchone()[0]
    print(f"作品总数: {total}")
    rows = con.execute(
        "SELECT platform, COUNT(*), AVG(views), AVG(likes), SUM(total_cost), "
        "SUM(video_generation_count), SUM(failed_generation_count) "
        "FROM content_experiments GROUP BY platform ORDER BY platform"
    ).fetchall()
    con.close()
    for p, n, avg_views, avg_likes, cost, vgen, fails in rows:
        print(
            f"  {p}: 作品 {n} | 平均播放 {avg_views or 0:.0f} | 平均点赞 {avg_likes or 0:.0f} "
            f"| 成本合计 {cost or 0:.2f} 元 | 生视频 {vgen or 0} 次 | 失败 {fails or 0} 次"
        )


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=DEFAULT_DB, help="SQLite 路径（默认 database/content_experiments.sqlite）")

    p = argparse.ArgumentParser(description="AI-MEDIA-OS 内容实验数据库")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", parents=[common], help="初始化数据库")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("add", parents=[common], help="新增 / 覆盖一条记录")
    sp.add_argument("json", help="JSON 字符串或 JSON 文件路径")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("import", parents=[common], help="从 CSV 导入")
    sp.add_argument("csv", help="CSV 文件路径")
    sp.set_defaults(func=cmd_import)

    sp = sub.add_parser("export", parents=[common], help="导出 CSV")
    sp.add_argument("--out", default=None, help="输出文件路径（默认 stdout）")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("list", parents=[common], help="列出全部记录")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("stats", parents=[common], help="基础统计")
    sp.set_defaults(func=cmd_stats)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
