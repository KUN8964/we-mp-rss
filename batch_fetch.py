#!/usr/bin/env python3
"""
批量补抓指定公众号的文章内容
用法: python3 batch_fetch.py MP_WXS_3869710678
"""
import sys
import os
import time

# 确保能在项目目录下运行
os.chdir('/Users/ngwa/we-mp-rss-local')
sys.path.insert(0, '/Users/ngwa/we-mp-rss-local')

from core.db import Db
from core.models import Article, DATA_STATUS
from core.article_content import sync_article_content, build_article_url
from core.config import cfg
from core.print import print_success, print_error, print_warning
from core.wait import Wait
import sqlalchemy

def batch_fetch_by_mp_id(mp_id: str, batch_size: int = 5, max_wait: int = 8):
    """
    批量补抓指定公众号的内容
    batch_size: 并发数（实际是串行，每批处理多少条后显示进度）
    max_wait: 每篇文章之间的等待秒数（避免被限流）
    """
    session = Db(tag="批量补抓").get_session()
    try:
        # 查询该公众号 content 为空的文章
        total = session.query(Article).filter(
            Article.mp_id == mp_id,
            Article.has_content == 0,
            Article.status != DATA_STATUS.DELETED,
        ).count()
        
        if total == 0:
            print_success(f"[{mp_id}] 所有文章已有内容，无需补抓")
            return
        
        print_success(f"[{mp_id}] 共 {total} 篇文章需要补抓内容")
        
        processed = 0
        success = 0
        failed = 0
        
        offset = 0
        while processed < total:
            articles = session.query(Article).filter(
                Article.mp_id == mp_id,
                Article.has_content == 0,
                Article.status != DATA_STATUS.DELETED,
            ).order_by(Article.publish_time.desc()).limit(batch_size).offset(offset).all()
            
            if not articles:
                break
            
            for art in articles:
                processed += 1
                try:
                    url = build_article_url(art)
                    if not url:
                        print_warning(f"  [{processed}/{total}] 无URL，跳过: {art.title[:30]}")
                        failed += 1
                        continue
                    
                    print(f"  [{processed}/{total}] 抓取: {art.title[:40]}", flush=True)
                    
                    updated, mode = sync_article_content(
                        session=session,
                        article=art,
                        preferred_mode=cfg.get("gather.content_mode", "web"),
                        force=True
                    )
                    
                    if updated and art.content and art.content.strip():
                        art.has_content = 1
                        art.status = DATA_STATUS.ACTIVE
                        session.commit()
                        success += 1
                        print_success(f"    ✅ 成功 (mode={mode})")
                    else:
                        failed += 1
                        print_error(f"    ❌ 失败 (mode={mode})")
                    
                    # 避免被限流
                    if processed < total:
                        wait_sec = min(max_wait, 3)
                        time.sleep(wait_sec)
                        
                except Exception as e:
                    failed += 1
                    print_error(f"    ❌ 异常: {e}")
                    session.rollback()
                    continue
            
            offset += batch_size
            print(f"  >>> 进度: {processed}/{total} (成功:{success}, 失败:{failed})", flush=True)
        
        print_success(f"[{mp_id}] 完成! 成功:{success}, 失败:{failed}, 总计:{processed}")
        
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 batch_fetch.py <mp_id>")
        sys.exit(1)
    
    target_mp_id = sys.argv[1]
    batch_fetch_by_mp_id(target_mp_id, batch_size=5, max_wait=5)
