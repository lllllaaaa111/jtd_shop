from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from .services import WechatAuthService
from .models import WechatUser
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def wechat_login(request):
    """
    微信小程序登录
    
    请求参数:
    {
        "code": "微信登录凭证",
        "user_info": {
            "nickName": "用户昵称",
            "avatarUrl": "头像URL",
            "gender": 1,
            "country": "国家",
            "province": "省份", 
            "city": "城市",
            "language": "语言"
        }
    }
    """
    try:
        code = request.data.get('code')
        user_info = request.data.get('user_info', {})
        
        if not code:
            return Response({
                'code': 400,
                'msg': '缺少登录凭证',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建微信认证服务
        wechat_service = WechatAuthService()
        
        # 通过code获取openid和session_key
        result = wechat_service.code2session(code)
        
        if not result['success']:
            return Response({
                'code': 401,
                'msg': result['error'],
                'result': None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        openid = result['openid']
        session_key = result['session_key']
        unionid = result.get('unionid')
        expires_in = result.get('expires_in', 7200)
        
        # 创建或更新微信用户
        wechat_user, created = wechat_service.create_or_update_wechat_user(
            openid=openid,
            session_key=session_key,
            unionid=unionid,
            user_info=user_info
        )
        
        # 保存会话信息
        wechat_service.save_session(openid, session_key, unionid, expires_in)
        
        # 登录用户
        login(request, wechat_user.user)
        
        return Response({
            'code': 200,
            'msg': '登录成功',
            'result': {
                'user_id': wechat_user.user.id,
                'username': wechat_user.user.username,
                'openid': openid,
                'nickname': wechat_user.nickname,
                'avatar_url': wechat_user.avatar_url,
                'is_new_user': created,
                'session_expires_in': expires_in
            }
        })
        
    except Exception as e:
        logger.exception("微信登录失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def wechat_code_login(request):
    """
    仅通过code登录（不获取用户信息）
    
    请求参数:
    {
        "code": "微信登录凭证"
    }
    """
    try:
        code = request.data.get('code')
        
        if not code:
            return Response({
                'code': 400,
                'msg': '缺少登录凭证',
                'result': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建微信认证服务
        wechat_service = WechatAuthService()
        
        # 通过code获取openid和session_key
        result = wechat_service.code2session(code)
        
        if not result['success']:
            return Response({
                'code': 401,
                'msg': result['error'],
                'result': None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        openid = result['openid']
        session_key = result['session_key']
        unionid = result.get('unionid')
        expires_in = result.get('expires_in', 7200)
        
        # 创建或更新微信用户（不更新用户信息）
        wechat_user, created = wechat_service.create_or_update_wechat_user(
            openid=openid,
            session_key=session_key,
            unionid=unionid
        )
        
        # 保存会话信息
        wechat_service.save_session(openid, session_key, unionid, expires_in)
        
        # 登录用户
        login(request, wechat_user.user)
        
        return Response({
            'code': 200,
            'msg': '登录成功',
            'result': {
                'user_id': wechat_user.user.id,
                'username': wechat_user.user.username,
                'openid': openid,
                'is_new_user': created,
                'session_expires_in': expires_in
            }
        })
        
    except Exception as e:
        logger.exception("微信登录失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_wechat_user_info(request):
    """
    更新微信用户信息
    
    请求参数:
    {
        "nickName": "用户昵称",
        "avatarUrl": "头像URL",
        "gender": 1,
        "country": "国家",
        "province": "省份",
        "city": "城市",
        "language": "语言"
    }
    """
    try:
        # 获取当前用户的微信信息
        try:
            wechat_user = WechatUser.objects.get(user=request.user)
        except WechatUser.DoesNotExist:
            return Response({
                'code': 404,
                'msg': '未找到微信用户信息',
                'result': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 更新用户信息
        user_info = request.data
        if user_info.get('nickName'):
            wechat_user.nickname = user_info['nickName']
        if user_info.get('avatarUrl'):
            wechat_user.avatar_url = user_info['avatarUrl']
        if 'gender' in user_info:
            wechat_user.gender = user_info['gender']
        if user_info.get('country'):
            wechat_user.country = user_info['country']
        if user_info.get('province'):
            wechat_user.province = user_info['province']
        if user_info.get('city'):
            wechat_user.city = user_info['city']
        if user_info.get('language'):
            wechat_user.language = user_info['language']
        
        wechat_user.save()
        
        return Response({
            'code': 200,
            'msg': '用户信息更新成功',
            'result': {
                'nickname': wechat_user.nickname,
                'avatar_url': wechat_user.avatar_url,
                'gender': wechat_user.gender,
                'country': wechat_user.country,
                'province': wechat_user.province,
                'city': wechat_user.city,
                'language': wechat_user.language
            }
        })
        
    except Exception as e:
        logger.exception("更新微信用户信息失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wechat_user_info(request):
    """
    获取当前用户的微信信息
    """
    try:
        # 获取当前用户的微信信息
        try:
            wechat_user = WechatUser.objects.get(user=request.user)
        except WechatUser.DoesNotExist:
            return Response({
                'code': 404,
                'msg': '未找到微信用户信息',
                'result': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'openid': wechat_user.openid,
                'nickname': wechat_user.nickname,
                'avatar_url': wechat_user.avatar_url,
                'gender': wechat_user.gender,
                'country': wechat_user.country,
                'province': wechat_user.province,
                'city': wechat_user.city,
                'language': wechat_user.language,
                'created_at': wechat_user.created_at,
                'updated_at': wechat_user.updated_at
            }
        })
        
    except Exception as e:
        logger.exception("获取微信用户信息失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def wechat_access_token(request):
    """
    获取微信小程序全局接口调用凭据
    """
    try:
        wechat_service = WechatAuthService()
        result = wechat_service.get_access_token()
        
        if not result['success']:
            return Response({
                'code': 500,
                'msg': result['error'],
                'result': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'code': 200,
            'msg': 'success',
            'result': {
                'access_token': result['access_token'],
                'expires_in': result['expires_in']
            }
        })
        
    except Exception as e:
        logger.exception("获取微信access_token失败")
        return Response({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'result': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 