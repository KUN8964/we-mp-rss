#!/usr/bin/env python3
"""手动抓取巫师财经的文章"""
import sys
import os

# 添加项目路径
sys.path.insert(0, '/Users/ngwa/we-mp-rss-local')

from core.db import DB
from core.models.feed import Feed
from core.wx import WxGather
from jobs.article import UpdateArticle, Update_Over
from core.print import print_info, print_success, print_error
from core.config import cfg

def main():
    print("=" * 80)
    print("开始抓取 巫师财经 的文章...")
    print("=" * 80)
    print()
    
    session = DB.get_session()
    try:
        # 查找巫师财经公众号
        feed = session.query(Feed).filter(Feed.mp_name == '巫师财经').first()
        
        if not feed:
            print("❌ 未找到 巫师财经 公众号")
            return False
        
        print(f"公众号: {feed.mp_name}")
        print(f"ID: {feed.id}")
        print(f"faker_id: {feed.faker_id}")
        print()
        
        # 初始化 WxGather
        wx = WxGather().Model()
        
        # 获取间隔
        interval = int(cfg.get("interval", 60))
        
        print(f"开始抓取文章（最多1页）...")
        print(f"抓取间隔: {interval} 秒")
        print()
        
        try:
            wx.get_Articles(
                feed.faker_id,
                CallBack=UpdateArticle,
                Mps_id=feed.id,
                Mps_title=feed.mp_name,
                MaxPage=1,  # 只抓取1页（约10篇文章）
                Over_CallBack=Update_Over,
                interval=interval
            )
            
            print()
            print("=" * 80)
            print(f"✅ 抓取完成！")
            print(f"共抓取 {wx.all_count()} 篇文章")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print_error(f"抓取失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    finally:
        session.close()

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
