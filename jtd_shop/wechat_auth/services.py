import requests
import json
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import WechatUser, WechatSession
from user_management.models import User

logger = logging.getLogger(__name__)

class WechatAuthService:
    """微信小程序认证服务"""
    
    def __init__(self):
        # 从settings获取微信小程序配置
        self.appid = getattr(settings, 'WECHAT_APPID', '')
        self.secret = getattr(settings, 'WECHAT_SECRET', '')
        self.code2session_url = 'https://api.weixin.qq.com/sns/jscode2session'
        self.access_token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    
    def code2session(self, code):
        """
        微信登录凭证校验
        通过 wx.login() 获取的 code 换取 openid 和 session_key
        
        Args:
            code: 微信登录凭证
            
        Returns:
            dict: 包含 openid, session_key, unionid 等信息
        """
        try:
            params = {
                'appid': self.appid,
                'secret': self.secret,
                'js_code': code,
                'grant_type': 'authorization_code'
            }
            
            response = requests.get(self.code2session_url, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result:
                logger.error(f"微信登录失败: {result}")
                return {
                    'success': False,
                    'error': result.get('errmsg', '微信登录失败'),
                    'errcode': result.get('errcode')
                }
            
            return {
                'success': True,
                'openid': result.get('openid'),
                'session_key': result.get('session_key'),
                'unionid': result.get('unionid'),
                'expires_in': result.get('expires_in', 7200)  # 默认2小时
            }
            
        except requests.RequestException as e:
            logger.error(f"微信API请求失败: {e}")
            return {
                'success': False,
                'error': '网络请求失败'
            }
        except Exception as e:
            logger.error(f"微信登录处理失败: {e}")
            return {
                'success': False,
                'error': '服务器内部错误'
            }
    
    def get_access_token(self):
        """
        获取微信小程序全局接口调用凭据
        
        Returns:
            dict: 包含 access_token 等信息
        """
        try:
            params = {
                'grant_type': 'client_credential',
                'appid': self.appid,
                'secret': self.secret
            }
            
            response = requests.get(self.access_token_url, params=params, timeout=10)
            result = response.json()
            
            if 'errcode' in result:
                logger.error(f"获取access_token失败: {result}")
                return {
                    'success': False,
                    'error': result.get('errmsg', '获取access_token失败'),
                    'errcode': result.get('errcode')
                }
            
            return {
                'success': True,
                'access_token': result.get('access_token'),
                'expires_in': result.get('expires_in', 7200)
            }
            
        except requests.RequestException as e:
            logger.error(f"获取access_token请求失败: {e}")
            return {
                'success': False,
                'error': '网络请求失败'
            }
        except Exception as e:
            logger.error(f"获取access_token处理失败: {e}")
            return {
                'success': False,
                'error': '服务器内部错误'
            }
    
    def create_or_update_wechat_user(self, openid, session_key, unionid=None, user_info=None):
        """
        创建或更新微信用户
        
        Args:
            openid: 微信OpenID
            session_key: 会话密钥
            unionid: 微信UnionID (可选)
            user_info: 用户信息 (可选)
            
        Returns:
            tuple: (wechat_user, created)
        """
        try:
            # 查找现有微信用户
            wechat_user, created = WechatUser.objects.get_or_create(
                openid=openid,
                defaults={
                    'unionid': unionid,
                    'session_key': session_key
                }
            )
            
            # 如果用户不存在，创建新用户
            if created:
                # 生成用户名
                username = f"wx_{openid[:8]}"
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"wx_{openid[:8]}_{counter}"
                    counter += 1
                
                # 创建Django用户
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@wechat.com",
                    password=User.objects.make_random_password()
                )
                
                wechat_user.user = user
                wechat_user.save()
                
                logger.info(f"创建新微信用户: {username}")
            else:
                # 更新会话密钥
                wechat_user.session_key = session_key
                if unionid:
                    wechat_user.unionid = unionid
                wechat_user.save()
            
            # 更新用户信息（如果提供）
            if user_info:
                wechat_user.nickname = user_info.get('nickName')
                wechat_user.avatar_url = user_info.get('avatarUrl')
                wechat_user.gender = user_info.get('gender', 0)
                wechat_user.country = user_info.get('country')
                wechat_user.province = user_info.get('province')
                wechat_user.city = user_info.get('city')
                wechat_user.language = user_info.get('language')
                wechat_user.save()
            
            return wechat_user, created
            
        except Exception as e:
            logger.error(f"创建或更新微信用户失败: {e}")
            raise
    
    def save_session(self, openid, session_key, unionid=None, expires_in=7200):
        """
        保存微信会话信息
        
        Args:
            openid: 微信OpenID
            session_key: 会话密钥
            unionid: 微信UnionID (可选)
            expires_in: 过期时间（秒）
        """
        try:
            expires_at = timezone.now() + timedelta(seconds=expires_in)
            
            # 删除过期的会话
            WechatSession.objects.filter(openid=openid).delete()
            
            # 创建新会话
            WechatSession.objects.create(
                openid=openid,
                session_key=session_key,
                unionid=unionid,
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"保存微信会话失败: {e}")
            raise
    
    def get_session(self, openid):
        """
        获取微信会话信息
        
        Args:
            openid: 微信OpenID
            
        Returns:
            WechatSession or None
        """
        try:
            session = WechatSession.objects.filter(openid=openid).first()
            if session and not session.is_expired:
                return session
            return None
        except Exception as e:
            logger.error(f"获取微信会话失败: {e}")
            return None 