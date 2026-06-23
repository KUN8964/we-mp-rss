"""
为指定公众号补抓所有缺失的文章内容
不依赖 Redis，直接同步执行
"""
import sys
import time
import random

sys.path.insert(0, '/Users/ngwa/we-mp-rss-local')

from core.db import DB
from core.config import cfg
from core.article_content import sync_article_content, build_article_url
from core.models.article import Article, DATA_STATUS
from core.print import print_success, print_error, print_warning

MP_ID = 'MP_WXS_3924611069'  # 酸酒公众号
MP_NAME = '酸酒'

def main():
    session = DB.get_session()
    try:
        # 查询没有 content 的文章
        articles = session.query(Article).filter(
            Article.mp_id == MP_ID,
            Article.content.is_(None),
            Article.status != DATA_STATUS.DELETED,
        ).order_by(Article.publish_time.desc()).all()
        
        total = len(articles)
        print(f"找到 {MP_NAME} 公众号 {total} 篇没有内容的文章")
        
        if total == 0:
            print("所有文章都已有内容，无需补抓")
            return
        
        success = 0
        failed = 0
        
        for i, article in enumerate(articles, 1):
            title = article.title or article.id
            print(f"\n[{i}/{total}] 处理: {title[:40]}")
            
            try:
                url = build_article_url(article)
                if not url:
                    print(f"  跳过：无法构建文章URL")
                    failed += 1
                    continue
                
                print(f"  URL: {url[:80]}")
                
                # 标记为抓取中
                original_status = article.status
                article.status = DATA_STATUS.FETCHING
                session.commit()
                
                # 抓取内容
                updated, fetch_mode = sync_article_content(
                    session=session,
                    article=article,
                    preferred_mode=cfg.get("gather.content_mode", "web"),
                )
                
                if updated:
                    if article.status == DATA_STATUS.DELETED:
                        print_error(f"  文章已被删除: {title}")
                    else:
                        print_success(f"  成功抓取 ({fetch_mode}): {title[:40]}")
                        success += 1
                    # 恢复原始状态
                    article.status = original_status
                    session.commit()
                else:
                    print_error(f"  抓取失败 ({fetch_mode})")
                    # 恢复状态以便重试
                    article.status = original_status
                    # 增加失败计数
                    article.fix_fail_count = (article.fix_fail_count or 0) + 1
                    session.commit()
                    failed += 1
                
                # 随机延迟，避免被封
                delay = random.randint(5, 15)
                print(f"  等待 {delay} 秒...")
                time.sleep(delay)
                
            except Exception as e:
                print_error(f"  处理出错: {e}")
                # 恢复状态
                try:
                    article.status = original_status
                    session.commit()
                except:
                    pass
                failed += 1
                time.sleep(5)
        
        print(f"\n\n完成！成功: {success}, 失败: {failed}, 总计: {total}")
        
    except Exception as e:
        print_error(f"程序出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    main()
