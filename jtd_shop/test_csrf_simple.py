#!/usr/bin/env python3
"""
简单的CSRF令牌测试脚本
专门测试新建订单接口的CSRF令牌使用
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USERNAME = "root"
PASSWORD = "Gg666666"

def test_csrf_token():
    """测试CSRF令牌获取和使用"""
    print("🔑 开始CSRF令牌测试...")
    
    s = requests.Session()
    
    # 1. 获取CSRF令牌
    print("\n📋 步骤1: 获取CSRF令牌")
    try:
        # 访问admin页面获取CSRF令牌
        resp = s.get(f"{BASE_URL}/admin/", timeout=10)
        if resp.status_code == 200:
            # 从cookies中获取
            if 'csrftoken' in s.cookies:
                csrf_token = s.cookies['csrftoken']
                print(f"✅ 获取到CSRF令牌: {csrf_token[:10]}...")
                print(f"令牌长度: {len(csrf_token)}")
            else:
                print("❌ 未在cookies中找到CSRF令牌")
                return False
        else:
            print(f"❌ 访问admin页面失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取CSRF令牌时发生错误: {str(e)}")
        return False
    
    # 2. 测试新建订单接口
    print("\n📋 步骤2: 测试新建订单接口")
    
    order_data = {
        "delivery_address": "北京市朝阳区某某街道123号",
        "recipient_name": "张三",
        "recipient_phone": "13800138000",
        "notes": "请尽快发货"
    }
    
    # 准备请求头
    headers = {
        'X-CSRFToken': csrf_token,
        'X-Csrftoken': csrf_token,  # Django也接受这个格式
        'Content-Type': 'application/json'
    }
    
    print(f"请求头: {headers}")
    print(f"请求数据: {json.dumps(order_data, ensure_ascii=False)}")
    
    try:
        # 使用Basic认证和CSRF令牌
        response = s.post(
            f"{BASE_URL}/orders/create/",
            json=order_data,
            headers=headers,
            auth=(USERNAME, PASSWORD),
            timeout=15
        )
        
        print(f"\n📊 响应结果:")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 接口调用成功！")
            try:
                result = response.json()
                print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {response.text}")
        elif response.status_code == 403:
            print("❌ 403 Forbidden - 可能是CSRF令牌问题")
            print(f"响应内容: {response.text}")
        else:
            print(f"❌ 接口调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保Django服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
    
    return True

if __name__ == "__main__":
    test_csrf_token() 