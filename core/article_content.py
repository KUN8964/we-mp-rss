from __future__ import annotations

from typing import Any, Tuple

from core.config import cfg
from core.models.base import DATA_STATUS
from core.print import print_info, print_warning


def normalize_content_mode(mode: str | None = None) -> str:
    normalized = (mode or cfg.get("gather.content_mode", "web") or "web").strip().lower()
    if normalized not in {"web", "api"}:
        return "web"
    return normalized


def extract_origin_article_id(article_id: str, mp_id: str | None = None) -> str:
    if not article_id:
        return ""

    mp_prefix = (mp_id or "").replace("MP_WXS_", "").strip()
    if mp_prefix:
        prefixed = f"{mp_prefix}-"
        if article_id.startswith(prefixed):
            return article_id[len(prefixed):]

    return article_id


def build_article_url(article: Any) -> str:
    article_url = (getattr(article, "url", "") or "").strip()
    if article_url:
        return article_url

    origin_id = extract_origin_article_id(
        getattr(article, "id", ""),
        getattr(article, "mp_id", ""),
    )
    if not origin_id:
        return ""

    return f"https://mp.weixin.qq.com/s/{origin_id}"


def _fetch_with_web(url: str) -> Tuple[str, Any]:
    from driver.wxarticle import Web

    result = Web.get_article_content(url) or {}
    return (result.get("content") or "").strip(),result


def _fetch_with_api(url: str) -> Tuple[str, Any]:
    from core.wx.model.api import MpsApi
    fetcher = MpsApi()
    return (fetcher.content_extract(url) or "").strip(),{}


def fetch_article_content(url: str, preferred_mode: str | None = None) -> Tuple[str, str, str, str]:
    mode = normalize_content_mode(preferred_mode)
    modes = [mode] + [item for item in ("web", "api") if item != mode]

    for current_mode in modes:
        try:
            if current_mode == "api":
                content, result = _fetch_with_api(url)
            else:
                content, result = _fetch_with_web(url)
            print(result)
            article_type = result.get("article_type", "")
            fetch_error = result.get("fetch_error", "")
        except Exception as exc:
            print_warning(f"fetch article content failed in {current_mode} mode: {exc}")
            continue

        if content == "DELETED":
            return content, current_mode, article_type, fetch_error
        if content:
            return content, current_mode, article_type, ""

    return "", mode, article_type, ""


def sync_article_content(
    session,
    article: Any,
    preferred_mode: str | None = None,
    force: bool = False,
) -> Tuple[bool, str]:
    existing_content = (getattr(article, "content", "") or "").strip()
    if existing_content and not force:
        if getattr(article, "has_content", 0) == 0:
            print_info(f"article {article.id} already has content, skipping fetch")
            article.has_content = 1
            session.commit()
            session.refresh(article)
            return True, "cached"
        return False, "cached"

    article_url = build_article_url(article)
    if not article_url:
        print_warning(f"article {getattr(article, 'id', '')} has no valid url")
        return False, "missing_url"

    content, mode, article_type, fetch_error = fetch_article_content(article_url, preferred_mode)
    if not content:
        return False, mode

    try:
        if content == "DELETED":
            # 区分"真的被删除"和"临时抓取失败"
            real_deleted = any(
                kw in (fetch_error or "")
                for kw in ["已被发布者删除", "内容审核中"]
            )
            if real_deleted:
                article.content = ""
                article.content_html = ""
                article.status = DATA_STATUS.DELETED
                article.has_content = 0
                session.commit()
                session.refresh(article)
                print_info(f"article {article.id} marked as DELETED (real) via {mode}")
            else:
                # 临时错误（反爬/限流/网络），只记录，不标记删除
                article.has_content = 0
                if hasattr(article, 'fetch_error'):
                    setattr(article, 'fetch_error', (fetch_error or "")[:500])
                session.commit()
                print_warning(f"article {article.id} fetch failed (temp error: {fetch_error}), not deleted")
            return True, mode
        
        # 检测违规文章（content 包含违规提示但未被标记为 DELETED）
        if content and any(kw in content for kw in ["违规无法查看", "违反《", "接相关投诉"]):
            print_warning(f"article {article.id} detected as VIOLATION (content contains violation keywords)")
            article.content = ""
            article.content_html = ""
            article.status = DATA_STATUS.DELETED
            article.has_content = 0
            if hasattr(article, 'fetch_error'):
                setattr(article, 'fetch_error', "该内容因违规无法查看")
            session.commit()
            session.refresh(article)
            print_info(f"article {article.id} marked as DELETED (violation) via {mode}")
            return True, "violation"
        
        from driver.wxarticle import Web
        from tools.fix import fix_html

        article.content = content
        article.content_html = fix_html(content)
        article.show_type=article_type or article.show_type
        article.status = DATA_STATUS.ACTIVE
        article.has_content = 1
        if not (getattr(article, "description", "") or "").strip():
            # 直接用全文作为 description，兼容只认 description 的 RSS 阅读器
            article.description = (content or "")[0:50000]
        # 修正成功,重置失败计数
        if hasattr(article, 'fix_fail_count'):
            article.fix_fail_count = 0
        session.commit()
        session.refresh(article)
        print_info(f"article {article.id} content synced via {mode}")
        return True, mode
    except Exception:
        # 修正失败,增加失败计数
        if hasattr(article, 'fix_fail_count'):
            article.fix_fail_count = (article.fix_fail_count or 0) + 1
            try:
                session.commit()
            except Exception:
                session.rollback()
        session.rollback()
        raise
