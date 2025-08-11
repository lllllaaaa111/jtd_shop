#!/usr/bin/env python3
"""
测试新建订单接口的脚本
"""
import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/orders/create/"

# 测试数据
test_data = {
    "delivery_address": "北京市朝阳区某某街道123号",
    "recipient_name": "张三",
    "recipient_phone": "13800138000",
    "shipping_address": "上海市浦东新区某某仓库",
    "notes": "请尽快发货",
    "payment_method": "alipay"
}

def test_create_order():
    """测试创建订单接口"""
    print("=== 测试新建订单接口 ===")
    print(f"接口地址: {API_ENDPOINT}")
    print(f"请求方法: POST")
    print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # 注意：这里需要有效的认证token
        # 在实际测试中，你需要先调用登录接口获取token
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer YOUR_TOKEN_HERE"  # 需要替换为实际的token
        }
        
        response = requests.post(
            API_ENDPOINT,
            json=test_data,
            headers=headers
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 接口调用成功！")
            result = response.json()
            print(f"响应数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print("❌ 接口调用失败！")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保Django服务器正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

def test_without_auth():
    """测试未认证访问"""
    print("\n=== 测试未认证访问 ===")
    try:
        response = requests.post(
            API_ENDPOINT,
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 401:
            print("✅ 认证检查正常，未认证用户被拒绝访问")
        else:
            print(f"❌ 认证检查异常，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_create_order()
    test_without_auth()
    
    print("\n=== 测试说明 ===")
    print("1. 要完整测试此接口，需要先调用登录接口获取认证token")
    print("2. 确保购物车中有商品")
    print("3. 确保Django服务器正在运行")
    print("4. 接口地址: POST /orders/create/")
    print("5. 必填字段: delivery_address, recipient_name, recipient_phone")
    print("6. 可选字段: shipping_address, notes, payment_method") 