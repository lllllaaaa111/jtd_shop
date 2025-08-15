#!/usr/bin/env python3
"""
测试CSRF认证接口
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_csrf_apis():
    """测试CSRF认证相关接口"""
    print("🔒 开始测试CSRF认证接口...")
    
    s = requests.Session()
    
    # 1. 获取CSRF信息
    print("\n📋 测试1: 获取CSRF信息")
    try:
        resp = s.get(f"{BASE_URL}/users/csrf/info/", timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("✅ 获取CSRF信息成功")
            print(f"CSRF令牌: {result['result']['csrf_token'][:10]}...")
            print(f"令牌长度: {result['result']['token_length']}")
            print(f"Cookie名称: {result['result']['cookie_name']}")
            print(f"请求头名称: {result['result']['header_name']}")
        else:
            print(f"❌ 获取CSRF信息失败: {resp.text}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 2. 获取CSRF令牌
    print("\n📋 测试2: 获取CSRF令牌")
    try:
        resp = s.get(f"{BASE_URL}/users/csrf/token/", timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("✅ 获取CSRF令牌成功")
            csrf_token = result['result']['csrf_token']
            print(f"CSRF令牌: {csrf_token[:10]}...")
            print(f"令牌长度: {result['result']['token_length']}")
            print(f"有效期: {result['result']['expires_in']}")
            print(f"使用说明: {result['result']['usage']}")
        else:
            print(f"❌ 获取CSRF令牌失败: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    
    # 3. 验证CSRF令牌
    print("\n📋 测试3: 验证CSRF令牌")
    try:
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        resp = s.post(f"{BASE_URL}/users/csrf/validate/", headers=headers, timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("✅ CSRF令牌验证成功")
            print(f"验证结果: {result['result']['valid']}")
            print(f"令牌长度: {result['result']['token_length']}")
        else:
            print(f"❌ CSRF令牌验证失败: {resp.text}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 4. 测试无效的CSRF令牌
    print("\n📋 测试4: 测试无效的CSRF令牌")
    try:
        headers = {
            'X-CSRFToken': 'invalid_token_123',
            'Content-Type': 'application/json'
        }
        
        resp = s.post(f"{BASE_URL}/users/csrf/validate/", headers=headers, timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 400:
            result = resp.json()
            print("✅ 无效令牌检测成功")
            print(f"验证结果: {result['result']['valid']}")
            print(f"错误信息: {result['msg']}")
        else:
            print(f"⚠️ 预期返回400，实际返回: {resp.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 5. 测试缺少CSRF令牌
    print("\n📋 测试5: 测试缺少CSRF令牌")
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        
        resp = s.post(f"{BASE_URL}/users/csrf/validate/", headers=headers, timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 400:
            result = resp.json()
            print("✅ 缺少令牌检测成功")
            print(f"错误信息: {result['msg']}")
        else:
            print(f"⚠️ 预期返回400，实际返回: {resp.status_code}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    # 6. 测试使用CSRF令牌进行登录
    print("\n📋 测试6: 使用CSRF令牌进行登录")
    try:
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        login_data = {
            "username": "root",
            "password": "Gg666666"
        }
        
        resp = s.post(f"{BASE_URL}/users/login/", json=login_data, headers=headers, timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            print("✅ 使用CSRF令牌登录成功")
            print(f"用户ID: {result['result']['user_id']}")
            print(f"用户名: {result['result']['username']}")
        else:
            print(f"❌ 登录失败: {resp.text}")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    
    return True

def test_csrf_with_orders():
    """测试CSRF令牌在订单接口中的使用"""
    print("\n🛒 测试CSRF令牌在订单接口中的使用...")
    
    s = requests.Session()
    
    # 1. 获取CSRF令牌
    try:
        resp = s.get(f"{BASE_URL}/users/csrf/token/", timeout=10)
        if resp.status_code == 200:
            csrf_token = resp.json()['result']['csrf_token']
            print(f"✅ 获取CSRF令牌: {csrf_token[:10]}...")
        else:
            print("❌ 获取CSRF令牌失败")
            return False
    except Exception as e:
        print(f"❌ 获取CSRF令牌失败: {str(e)}")
        return False
    
    # 2. 使用CSRF令牌测试新建订单接口
    try:
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        order_data = {
            "delivery_address": "北京市朝阳区某某街道123号",
            "recipient_name": "张三",
            "recipient_phone": "13800138000",
            "notes": "测试CSRF令牌"
        }
        
        resp = s.post(f"{BASE_URL}/orders/create/", json=order_data, headers=headers, auth=('root', 'Gg666666'), timeout=15)
        print(f"订单接口状态码: {resp.status_code}")
        
        if resp.status_code == 400:
            result = resp.json()
            if "购物车为空" in result.get('msg', ''):
                print("✅ CSRF令牌在订单接口中工作正常")
                print(f"返回信息: {result['msg']}")
            else:
                print(f"⚠️ 返回其他业务错误: {result.get('msg')}")
        elif resp.status_code == 403:
            print("❌ CSRF令牌验证失败")
        else:
            print(f"⚠️ 返回其他状态码: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 CSRF认证接口测试")
    print("=" * 50)
    
    # 测试CSRF认证接口
    test_csrf_apis()
    
    # 测试CSRF令牌在订单接口中的使用
    test_csrf_with_orders()
    
    print("\n" + "=" * 50)
    print("📊 测试完成") 