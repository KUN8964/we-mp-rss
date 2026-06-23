#!/usr/bin/env python3
"""
巫师财经文章正文补抓脚本 v2

修复内容：
- 清除了已抓取的 JS 空壳文章内容
- 增加了页面加载等待时间 (max 30s 等待正文渲染)
- 抓取后验证内容质量（检测 JS 空壳）
"""

import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.db import DB
from core.models.article import Article
from core.models.base import DATA_STATUS
from core.article_content import sync_article_content
from core.print import print_info, print_success, print_error, print_warning

def main():
    session = DB.get_session()

    # 查询巫师财经需要补抓的文章
    articles = session.query(Article).filter(
        Article.mp_id == "MP_WXS_3533686744",
        Article.has_content == 0,
        Article.status == DATA_STATUS.ACTIVE,
    ).order_by(Article.publish_time.desc()).all()

    total = len(articles)
    print_info(f"共 {total} 篇文章需要补抓正文")

    success = 0
    failed = 0

    for i, article in enumerate(articles):
        title = (getattr(article, 'title', '') or '')[:50]
        print_info(f"\n[{i+1}/{total}] {title}")

        try:
            result, mode = sync_article_content(
                session, article, preferred_mode="web", force=True
            )
            if result:
                success += 1
                print_success(f"  ✅ 成功 ({mode})")
            else:
                failed += 1
                print_warning(f"  ⚠️ 失败 ({mode})")
        except Exception as e:
            failed += 1
            print_error(f"  ❌ 异常: {e}")
            try:
                session.rollback()
            except Exception:
                pass

        # 每篇间隔 10-25 秒，避免触发反爬
        delay = random.uniform(10, 25)
        if i < total - 1:
            print_info(f"  等待 {delay:.0f}s...")
            time.sleep(delay)

    print_info(f"\n========== 完成 ==========")
    print_success(f"成功: {success}/{total}")
    print_warning(f"失败: {failed}/{total}")

    session.close()


if __name__ == "__main__":
    main()
