"""
微信服务门面层 (Service Facade)

统一封装所有 driver 层微信操作，提供稳定的业务接口。
API 层 (apis/) 只依赖此模块，不再直接 import driver/*。

职责：
- 二维码登录认证 (QR code auth)
- 微信账号切换
- Token / 登录状态查询
- 文章抓取器获取
"""

import asyncio
from typing import Any, Dict, Optional

from core.print import print_info, print_error


# ============================
# 二维码认证相关
# ============================

def get_qr_code(callback: Any = None) -> dict:
    """生成微信登录二维码，返回 {code, is_exists}"""
    from driver.wx import WX_API
    from driver.success import Success as _Success
    return WX_API.GetCode(callback=_Success)


def get_qr_image_exists() -> bool:
    """检查二维码图片是否已生成"""
    from driver.wx import WX_API
    return WX_API.GetHasCode()


def get_qr_status() -> dict:
    """获取扫码状态"""
    from driver.wx import WX_API
    return WX_API.QrStatus()


async def close_wx_session() -> dict:
    """关闭微信浏览器会话"""
    from driver.wx import WX_API
    result = await WX_API.Close()
    return {"closed": result} if result else {"closed": False}


async def switch_wechat_account() -> bool:
    """切换微信公众号账号"""
    from driver.wx import WX_API
    return await WX_API.switch_account()


# ============================
# Token / 登录状态
# ============================

def get_wx_token(key: str = "token", default: str = "") -> str:
    """获取微信 Token"""
    from driver.token import get as _get
    return str(_get(key, default))


def get_wx_login_status() -> bool:
    """获取微信登录状态"""
    from driver.success import getStatus
    return getStatus()


def get_wx_login_info() -> Optional[dict]:
    """获取微信登录信息"""
    from driver.success import getLoginInfo
    return getLoginInfo()


def get_wx_cfg() -> dict:
    """获取微信 Token 配置"""
    from driver.token import wx_cfg
    return wx_cfg


# ============================
# 文章抓取
# ============================

def get_article_fetcher():
    """获取文章抓取器实例"""
    from driver.wxarticle import WXArticleFetcher
    return WXArticleFetcher()


# ============================
# 文章展示 (Web View)
# ============================

def get_web_viewer():
    """获取文章 Web 展示器类（提供静态方法 get_image_url, proxy_images, get_description）"""
    from driver.wxarticle import Web
    return Web


# ============================
# 登录状态管理
# ============================

def set_wx_login_status(status: bool):
    """设置微信登录状态"""
    from driver.success import setStatus
    setStatus(status)


def can_get_wx_token() -> Any:
    """检查是否可以获取 Token"""
    from driver.success import CanGetToken
    return CanGetToken


# ============================
# 文章内容操作
# ============================

def get_article_content_sync(url: str) -> dict:
    """获取文章内容（同步包装器）"""
    from driver.wxarticle import Web
    return Web.get_article_content(url)


def clean_article_html(html_content: str) -> str:
    """清洗文章 HTML"""
    from driver.wxarticle import Web
    return Web.clean_article_content(str(html_content))


# ============================
# 二维码/登录回调
# ============================

def get_qr_code_with_callback(callback=None, notice=None) -> dict:
    """生成微信登录二维码，带自定义回调"""
    from driver.wx import WX_API
    return WX_API.GetCode(CallBack=callback, Notice=notice)


def get_qr_code_url() -> str:
    """获取二维码图片 URL"""
    from driver.wx import WX_API
    qr = WX_API.QRcode()
    return str(qr.get('code', '')) if qr else ''
