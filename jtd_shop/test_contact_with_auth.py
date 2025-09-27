#!/usr/bin/env python3
"""
测试修改用户联系方式接口（带认证）
"""

import requests
import json
import sys

# 配置
BASE_URL = "https://backend.jintiandeshop.cn"
CSRF_URL = f"{BASE_URL}/users/csrf/token/"
LOGIN_URL = f"{BASE_URL}/users/login/"
CONTACT_UPDATE_URL = f"{BASE_URL}/users/contact/update/"

def get_csrf_token():
    """获取CSRF token"""
    try:
        response = requests.get(CSRF_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                return data.get('result', {}).get('csrf_token')
        print(f"获取CSRF token失败: {response.text}")
        return None
    except Exception as e:
        print(f"获取CSRF token异常: {e}")
        return None

def login_user(username, password):
    """用户登录"""
    try:
        csrf_token = get_csrf_token()
        if not csrf_token:
            print("无法获取CSRF token")
            return None
        
        session = requests.Session()
        
        # 先获取CSRF token
        csrf_response = session.get(CSRF_URL)
        if csrf_response.status_code == 200:
            csrf_data = csrf_response.json()
            if csrf_data.get('code') == 200:
                csrf_token = csrf_data.get('result', {}).get('csrf_token')
        
        # 登录
        login_data = {
            "username": username,
            "password": password
        }
        
        response = session.post(
            LOGIN_URL,
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print(f"登录成功: {data.get('result', {}).get('username')}")
                return session
            else:
                print(f"登录失败: {data.get('msg')}")
        else:
            print(f"登录HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
        
        return None
        
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_update_contact_with_auth():
    """测试带认证的联系方式更新"""
    print("=" * 60)
    print("测试修改用户联系方式接口（带认证）")
    print("=" * 60)
    
    # 尝试登录（这里使用测试用户，实际使用时需要有效的用户名密码）
    print("\n尝试登录...")
    session = login_user("admin", "admin123")  # 请替换为实际的用户名密码
    
    if not session:
        print("❌ 无法登录，跳过认证测试")
        print("请确保有有效的用户账号，或修改脚本中的用户名密码")
        return
    
    # 测试1: 更新手机号
    print("\n1. 测试更新手机号")
    test_data_1 = {
        "phone": "13800138000"
    }
    
    try:
        response = session.put(
            CONTACT_UPDATE_URL,
            json=test_data_1,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 手机号更新成功")
                result = data.get('result', {})
                print(f"更新后的手机号: {result.get('phone')}")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试2: 更新邮箱
    print("\n2. 测试更新邮箱")
    test_data_2 = {
        "email": "test@example.com"
    }
    
    try:
        response = session.put(
            CONTACT_UPDATE_URL,
            json=test_data_2,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 邮箱更新成功")
                result = data.get('result', {})
                print(f"更新后的邮箱: {result.get('email')}")
            else:
                print(f"❌ 业务错误: {data.get('msg')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    # 测试3: 无效手机号格式
    print("\n3. 测试无效手机号格式")
    test_data_3 = {
        "phone": "123456789"  # 无效格式
    }
    
    try:
        response = session.put(
            CONTACT_UPDATE_URL,
            json=test_data_3,
            headers={'Content-Type': 'application/json'},
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
    
    # 测试4: 无效邮箱格式
    print("\n4. 测试无效邮箱格式")
    test_data_4 = {
        "email": "invalid-email"  # 无效格式
    }
    
    try:
        response = session.put(
            CONTACT_UPDATE_URL,
            json=test_data_4,
            headers={'Content-Type': 'application/json'},
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

def test_without_auth():
    """测试未认证访问"""
    print("\n" + "=" * 60)
    print("测试未认证访问")
    print("=" * 60)
    
    try:
        response = requests.put(
            CONTACT_UPDATE_URL,
            json={"phone": "13800138000"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 403:
            print("✅ 正确要求认证")
        else:
            print(f"❌ 应该要求认证，实际返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def main():
    """主函数"""
    print("开始测试修改用户联系方式接口")
    print(f"测试URL: {CONTACT_UPDATE_URL}")
    
    # 测试未认证访问
    test_without_auth()
    
    # 测试带认证的访问
    test_update_contact_with_auth()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n注意：")
    print("1. 如需测试认证功能，请确保有有效的用户账号")
    print("2. 可以修改脚本中的用户名密码进行测试")
    print("3. 接口支持PUT和PATCH方法")
    print("4. 支持的字段：phone, email, first_name, last_name")

if __name__ == "__main__":
    main()
