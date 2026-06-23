#!/usr/bin/env python3
"""
为 UNFOLLOW威士忌 公众号补抓缺失的文章内容
"""
import sys
import os
import time
import random

# 添加项目路径
sys.path.insert(0, '/Users/ngwa/we-mp-rss-local')

from core.article_content import sync_article_content
from core.db import DB
from core.models.article import Article

# UNFOLLOW威士忌 公众号ID
MP_ID = 'MP_WXS_3869710678'
MP_NAME = 'UNFOLLOW威士忌'

def main():
    print(f"📊 开始为 [{MP_NAME}] 补抓缺失的文章内容...")
    
    session = DB.get_session()
    success_count = 0
    failed_count = 0
    deleted_count = 0
    
    try:
        # 查询没有 content 的文章
        articles = session.query(Article).filter(
            Article.mp_id == MP_ID,
            Article.content.is_(None),
            Article.status != 6,  # 不是已删除
        ).order_by(Article.publish_time.desc()).all()
        
        total = len(articles)
        print(f"找到 {total} 篇需要补抓的文章")
        print(f"预计需要时间：{total * 8 // 60} 分钟（每篇约8秒）")
        print("=" * 80)
        
        for idx, article in enumerate(articles, 1):
            print(f"\n[{idx}/{total}] 处理: {article.title[:50]}...")
            print(f"  URL: {article.url}")
            
            try:
                # 抓取内容
                result = sync_article_content(session, article, force=True)
                
                # result 是 Tuple[bool, str]
                if result and result[0]:  # 第一个返回值是成功标志
                    if result[1] == "cached":
                        print(f"  ✅ 已有内容（缓存）")
                        success_count += 1
                    elif result[1] == "DELETED":
                        print(f"  ⚠️ 已被删除: {result[1]}")
                        deleted_count += 1
                    else:
                        print(f"  ✅ 抓取成功 (模式: {result[1]})")
                        success_count += 1
                else:
                    error_msg = result[1] if result else "unknown"
                    print(f"  ❌ 抓取失败: {error_msg}")
                    failed_count += 1
                
                # 每篇之间随机延迟（避免反爬）
                if idx < total:
                    delay = random.randint(5, 15)
                    print(f"  等待 {delay} 秒...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
                failed_count += 1
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'='*80}")
        print(f"✅ 补抓完成！")
        print(f"成功: {success_count}/{total}")
        print(f"失败: {failed_count}/{total}")
        print(f"已删除: {deleted_count}/{total}")
        print(f"{'='*80}")
        
        return success_count
        
    finally:
        session.close()

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success > 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
