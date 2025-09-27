#!/usr/bin/env python3
"""
测试修改用户联系方式接口
测试接口: PUT/PATCH /users/contact/update/
"""

import requests
import json
import sys

# 配置
BASE_URL = "https://backend.jintiandeshop.cn"
CONTACT_UPDATE_URL = f"{BASE_URL}/users/contact/update/"

def test_update_contact():
    """测试修改用户联系方式接口"""
    print("=" * 60)
    print("测试修改用户联系方式接口")
    print("=" * 60)
    
    # 测试用例1: 正常更新手机号
    print("\n1. 测试正常更新手机号")
    test_data_1 = {
        "phone": "13800138000"
    }
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json=test_data_1,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'  # 实际使用时需要获取真实的CSRF token
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 手机号更新成功")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试用例2: 正常更新邮箱
    print("\n2. 测试正常更新邮箱")
    test_data_2 = {
        "email": "test@example.com"
    }
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json=test_data_2,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 邮箱更新成功")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试用例3: 同时更新手机号和邮箱
    print("\n3. 测试同时更新手机号和邮箱")
    test_data_3 = {
        "phone": "13900139000",
        "email": "user@example.com",
        "first_name": "张",
        "last_name": "三"
    }
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json=test_data_3,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 联系方式更新成功")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试用例4: 无效手机号格式
    print("\n4. 测试无效手机号格式")
    test_data_4 = {
        "phone": "123456789"  # 无效格式
    }
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json=test_data_4,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get('code') == 400:
                print("✅ 正确识别无效手机号格式")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ 应该返回400错误，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试用例5: 无效邮箱格式
    print("\n5. 测试无效邮箱格式")
    test_data_5 = {
        "email": "invalid-email"  # 无效格式
    }
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json=test_data_5,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if data.get('code') == 400:
                print("✅ 正确识别无效邮箱格式")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ 应该返回400错误，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试用例6: 使用PATCH方法
    print("\n6. 测试PATCH方法")
    test_data_6 = {
        "phone": "13700137000"
    }
    
    try:
        response = requests.patch(
            CONTACT_UPDATE_URL,
            json=test_data_6,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'
            },
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ PATCH方法更新成功")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_with_authentication():
    """测试需要认证的情况"""
    print("\n" + "=" * 60)
    print("测试认证相关功能")
    print("=" * 60)
    
    # 测试未认证访问
    print("\n1. 测试未认证访问")
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json={"phone": "13800138000"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 401:
            print("✅ 正确要求认证")
        else:
            print(f"❌ 应该要求认证，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def main():
    """主函数"""
    print("开始测试修改用户联系方式接口")
    print(f"测试URL: {CONTACT_UPDATE_URL}")
    
    # 基础功能测试
    test_update_contact()
    
    # 认证测试
    test_with_authentication()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
