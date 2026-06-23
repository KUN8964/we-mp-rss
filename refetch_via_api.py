#!/usr/bin/env python3
"""
通过服务 API 补抓巫师财经文章正文

与 standone 脚本不同，此脚本通过已认证的服务 API 调用来抓取内容，
利用服务已有的微信会话和 Playwright 浏览器实例，避免反爬检测。
"""

import sys
import os
import time
import random
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

API_BASE = "http://localhost:8001/api/v1/wx"
MP_ID = "MP_WXS_3533686744"

# 先从 DB 获取所有需要补抓的文章
from core.db import DB
from core.models.article import Article
from core.models.base import DATA_STATUS

session = DB.get_session()
articles = session.query(Article).filter(
    Article.mp_id == MP_ID,
    Article.has_content == 0,
    Article.status == DATA_STATUS.ACTIVE,
).order_by(Article.publish_time.desc()).all()

total = len(articles)
print(f"共 {total} 篇文章需要补抓")

success = 0
failed = 0

for i, article in enumerate(articles):
    title = (article.title or "")[:50]
    aid = article.id
    print(f"\n[{i+1}/{total}] {title}")

    try:
        # 调用服务 API 刷新文章内容
        resp = requests.post(
            f"{API_BASE}/articles/{aid}/refresh?mode=web",
            timeout=120,
        )
        data = resp.json() if resp.text else {}
        code = data.get("code", -1)

        if code == 0:
            success += 1
            print(f"  ✅ 成功")
        elif code == 40101:
            print(f"  ⚠️ 需登录验证")
        else:
            failed += 1
            msg = data.get("detail", {}).get("message", str(data)[:80])
            print(f"  ⚠️ 失败: {msg}")
    except requests.exceptions.Timeout:
        failed += 1
        print(f"  ❌ 超时")
    except Exception as e:
        failed += 1
        print(f"  ❌ 异常: {e}")

    # 间隔 20-40 秒
    if i < total - 1:
        delay = random.uniform(20, 40)
        print(f"  等待 {delay:.0f}s...")
        time.sleep(delay)

session.close()
print(f"\n========== 完成 ==========")
print(f"成功: {success}/{total}")
print(f"失败: {failed}/{total}")
