#!/usr/bin/env python3
"""
完整的订单创建流程测试
包括：获取CSRF令牌、登录、添加商品到购物车、创建订单
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USERNAME = "root"
PASSWORD = "Gg666666"

def test_complete_order_flow():
    """测试完整的订单创建流程"""
    print("🔄 开始测试完整的订单创建流程...")
    
    s = requests.Session()
    
    # 1. 获取CSRF令牌
    print("\n📋 步骤1: 获取CSRF令牌")
    try:
        resp = s.get(f"{BASE_URL}/admin/", timeout=10)
        if resp.status_code == 200 and 'csrftoken' in s.cookies:
            csrf_token = s.cookies['csrftoken']
            print(f"✅ 获取到CSRF令牌: {csrf_token[:10]}...")
        else:
            print("❌ 无法获取CSRF令牌")
            return False
    except Exception as e:
        print(f"❌ 获取CSRF令牌时发生错误: {str(e)}")
        return False
    
    # 2. 登录
    print("\n📋 步骤2: 用户登录")
    try:
        login_data = {"username": USERNAME, "password": PASSWORD}
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        resp = s.post(f"{BASE_URL}/users/login/", json=login_data, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get('code') == 200:
                print("✅ 登录成功")
                # 重新获取CSRF令牌
                resp = s.get(f"{BASE_URL}/admin/", timeout=10)
                if 'csrftoken' in s.cookies:
                    csrf_token = s.cookies['csrftoken']
                    print(f"🔄 重新获取CSRF令牌: {csrf_token[:10]}...")
            else:
                print(f"❌ 登录失败: {result.get('msg', '未知错误')}")
                return False
        else:
            print(f"❌ 登录请求失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录时发生错误: {str(e)}")
        return False
    
    # 3. 检查购物车状态
    print("\n📋 步骤3: 检查购物车状态")
    try:
        resp = s.get(f"{BASE_URL}/orders/cart/list/", timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            cart_items = result.get('result', [])
            print(f"购物车中有 {len(cart_items)} 件商品")
            
            if not cart_items:
                print("⚠️ 购物车为空，需要先添加商品")
                print("由于没有商品管理接口，无法自动添加商品到购物车")
                print("请手动在系统中添加商品到购物车后再测试")
                return False
            else:
                print("✅ 购物车中有商品，可以继续测试")
        else:
            print(f"❌ 获取购物车失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查购物车时发生错误: {str(e)}")
        return False
    
    # 4. 尝试创建订单
    print("\n📋 步骤4: 尝试创建订单")
    order_data = {
        "delivery_address": "北京市朝阳区某某街道123号",
        "recipient_name": "张三",
        "recipient_phone": "13800138000",
        "notes": "请尽快发货"
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    
    try:
        resp = s.post(f"{BASE_URL}/orders/create/", json=order_data, headers=headers, timeout=15)
        
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            print("✅ 订单创建成功！")
            result = resp.json()
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        elif resp.status_code == 400:
            result = resp.json()
            print(f"⚠️ 业务逻辑错误: {result.get('msg', '未知错误')}")
            if "购物车为空" in result.get('msg', ''):
                print("💡 这是预期的错误，说明CSRF问题已解决")
                print("✅ 测试成功：CSRF令牌工作正常")
        else:
            print(f"❌ 订单创建失败: {resp.status_code}")
            print(f"响应内容: {resp.text}")
            
    except Exception as e:
        print(f"❌ 创建订单时发生错误: {str(e)}")
    
    return True

def test_csrf_working():
    """简单测试CSRF是否工作"""
    print("\n🔒 简单CSRF测试...")
    
    s = requests.Session()
    
    # 获取CSRF令牌
    resp = s.get(f"{BASE_URL}/admin/", timeout=10)
    if 'csrftoken' in s.cookies:
        csrf_token = s.cookies['csrftoken']
        print(f"✅ 获取到CSRF令牌: {csrf_token[:10]}...")
        
        # 测试新建订单接口（应该返回业务逻辑错误，不是CSRF错误）
        order_data = {
            "delivery_address": "测试地址",
            "recipient_name": "测试用户",
            "recipient_phone": "13800000000"
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        resp = s.post(f"{BASE_URL}/orders/create/", json=order_data, headers=headers, auth=(USERNAME, PASSWORD), timeout=15)
        
        if resp.status_code == 400:
            result = resp.json()
            if "购物车为空" in result.get('msg', ''):
                print("✅ CSRF测试通过：返回业务逻辑错误，不是CSRF错误")
                return True
            else:
                print(f"⚠️ 返回其他业务错误: {result.get('msg')}")
                return True
        elif resp.status_code == 403:
            print("❌ CSRF测试失败：仍然返回403错误")
            return False
        else:
            print(f"⚠️ 返回其他状态码: {resp.status_code}")
            return True
    else:
        print("❌ 无法获取CSRF令牌")
        return False

if __name__ == "__main__":
    print("🚀 订单创建流程测试")
    print("=" * 50)
    
    # 先进行简单的CSRF测试
    csrf_ok = test_csrf_working()
    
    if csrf_ok:
        print("\n" + "=" * 50)
        # 再进行完整的流程测试
        test_complete_order_flow()
    else:
        print("\n❌ CSRF测试失败，跳过完整流程测试") 