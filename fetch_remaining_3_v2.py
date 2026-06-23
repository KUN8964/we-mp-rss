#!/usr/bin/env python3
"""
补抓剩余3篇文章的内容（修正版）
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

# 剩余3篇文章的ID
REMAINING_ARTICLES = [
    '3924611069-2247486391_1',
    '3924611069-2247486200_1',
    '3924611069-2247485818_1'
]

def main():
    print(f"📊 开始补抓剩余 {len(REMAINING_ARTICLES)} 篇文章...")
    
    session = DB.get_session()
    success_count = 0
    
    try:
        for idx, article_id in enumerate(REMAINING_ARTICLES, 1):
            print(f"\n[{idx}/{len(REMAINING_ARTICLES)}] 处理: {article_id}")
            
            try:
                # 查询文章对象
                article = session.query(Article).filter(Article.id == article_id).first()
                
                if not article:
                    print(f"  ⚠️ 文章不存在: {article_id}")
                    continue
                
                print(f"  标题: {article.title}")
                print(f"  URL: {article.url}")
                
                # 正确调用：传递 session 和 article 对象
                print(f"  正在抓取内容...")
                result = sync_article_content(session, article, force=True)
                
                # result 是 Tuple[bool, str]
                if result and result[0]:  # 第一个返回值是成功标志
                    print(f"  ✅ 抓取成功 (模式: {result[1]})")
                    success_count += 1
                else:
                    error_msg = result[1] if result else "unknown"
                    print(f"  ❌ 抓取失败: {error_msg}")
                
                # 每篇之间随机延迟（避免反爬）
                if idx < len(REMAINING_ARTICLES):
                    delay = random.randint(5, 10)
                    print(f"  等待 {delay} 秒...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ❌ 错误: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n{'='*80}")
        print(f"✅ 补抓完成！")
        print(f"成功: {success_count}/{len(REMAINING_ARTICLES)}")
        print(f"{'='*80}")
        
        return success_count
        
    finally:
        session.close()

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success == len(REMAINING_ARTICLES) else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
