"""补抓巫师财经公众号文章正文内容"""
import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.db import DB
from core.models.feed import Feed
from core.models.article import Article
from core.models.base import DATA_STATUS
from core.article_content import sync_article_content

db = DB.get_session()

# 查找巫师财经
feed = db.query(Feed).filter(Feed.mp_name.like('%巫师%')).first()
if not feed:
    print("未找到巫师财经公众号")
    sys.exit(1)

print(f"公众号: {feed.mp_name} (ID: {feed.id})")

# 查找无内容的文章（status != DELETED 且 has_content == 0）
no_content_articles = db.query(Article).filter(
    Article.mp_id == feed.id,
    Article.has_content == 0,
    Article.status != 1000,  # DATA_STATUS.DELETED = 1000
    Article.url != None,
    Article.url != ''
).order_by(Article.publish_time.desc()).all()

print(f"需要补抓的文章数量: {len(no_content_articles)}")

success_count = 0
skip_count = 0
error_count = 0

for i, article in enumerate(no_content_articles):
    title = article.title[:40] if article.title else f"ID:{article.id}"
    print(f"\n[{i+1}/{len(no_content_articles)}] 正在抓取: {title}")
    
    try:
        result, mode = sync_article_content(db, article, preferred_mode="web", force=True)
        if result:
            success_count += 1
            print(f"  ✅ 抓取成功 (mode={mode})")
        else:
            skip_count += 1
            print(f"  ⏭️ 跳过 (reason={mode})")
    except Exception as e:
        error_count += 1
        print(f"  ❌ 错误: {str(e)[:80]}")
        db.rollback()
    
    # 随机延迟 5-15 秒，规避反爬
    delay = random.randint(5, 15)
    print(f"  等待 {delay} 秒...")
    time.sleep(delay)

print(f"\n========== 补抓完成 ==========")
print(f"成功: {success_count}, 跳过: {skip_count}, 错误: {error_count}")

db.close()
