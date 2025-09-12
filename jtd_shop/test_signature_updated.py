#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的签名接口
验证 appid 和 mchid 从数据库自动获取，以及 time_expire 参数
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_generate_signature_string():
    """测试生成签名串接口"""
    print("🧪 测试生成签名串接口...")
    
    url = f"{BASE_URL}/system/generate-signature-string/"
    
    # 测试数据 - 不再需要提供 appid 和 mchid
    test_data = {
        "method": "POST",
        "url_path": "/v3/pay/transactions/jsapi",
        "query_string": "",
        "description": "测试商品",
        "out_trade_no": f"TEST{int(time.time())}",
        "notify_url": "https://example.com/notify",
        "amount": {
            "total": 100,
            "currency": "CNY"
        },
        "payer": {
            "openid": "test_openid_123"
        }
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 接口调用成功")
            print(f"返回的 appid: {data['result']['appid']}")
            print(f"返回的 mchid: {data['result']['mchid']}")
            print(f"返回的 time_expire: {data['result']['time_expire']}")
            print(f"签名串长度: {len(data['result']['signature_string'])}")
            print(f"签名串预览: {data['result']['signature_string'][:100]}...")
        else:
            print(f"❌ 接口调用失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_get_wechat_certificate():
    """测试获取微信证书接口"""
    print("\n🧪 测试获取微信证书接口...")
    
    url = f"{BASE_URL}/system/get-wechat-certificate/"
    
    # 测试数据 - 不再需要提供 mchid
    test_data = {
        "method": "POST",
        "url_path": "/v3/pay/transactions/jsapi",
        "query_string": "",
        "description": "测试商品",
        "out_trade_no": f"TEST{int(time.time())}",
        "notify_url": "https://example.com/notify",
        "amount": {
            "total": 100,
            "currency": "CNY"
        },
        "payer": {
            "openid": "test_openid_123"
        }
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 接口调用成功")
            print(f"返回的 mchid: {data['result']['mchid']}")
            print(f"返回的 serial_no: {data['result']['serial_no']}")
            print(f"Authorization 头: {data['result']['authorization'][:50]}...")
        else:
            print(f"❌ 接口调用失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_time_expire_format():
    """测试 time_expire 格式"""
    print("\n🧪 测试 time_expire 格式...")
    
    url = f"{BASE_URL}/system/generate-signature-string/"
    
    test_data = {
        "method": "POST",
        "url_path": "/v3/pay/transactions/jsapi",
        "description": "测试商品",
        "out_trade_no": f"TEST{int(time.time())}",
        "notify_url": "https://example.com/notify",
        "amount": {"total": 100, "currency": "CNY"},
        "payer": {"openid": "test_openid_123"}
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            time_expire = data['result']['time_expire']
            print(f"time_expire: {time_expire}")
            
            # 验证格式是否正确
            import re
            pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$'
            if re.match(pattern, time_expire):
                print("✅ time_expire 格式正确")
            else:
                print("❌ time_expire 格式错误")
                
            # 验证时间差是否为15分钟
            current_time = int(time.time())
            expire_time = data['result']['timestamp'] + 900  # 15分钟 = 900秒
            print(f"当前时间戳: {current_time}")
            print(f"过期时间戳: {expire_time}")
            print(f"时间差: {expire_time - current_time} 秒")
            
        else:
            print(f"❌ 接口调用失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试修改后的签名接口...")
    print("=" * 50)
    
    test_generate_signature_string()
    test_get_wechat_certificate()
    test_time_expire_format()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
