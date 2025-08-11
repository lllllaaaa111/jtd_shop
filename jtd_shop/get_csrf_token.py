#!/usr/bin/env python3
"""
CSRF令牌获取工具
用于测试和调试CSRF令牌获取过程
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

def get_csrf_token():
    """获取CSRF令牌的详细过程"""
    print("🔑 开始获取CSRF令牌...")
    
    s = requests.Session()
    
    # 方法1: 从admin页面获取
    print("\n📋 方法1: 从admin页面获取")
    try:
        url = urljoin(BASE_URL + '/', 'admin/')
        print(f"访问URL: {url}")
        resp = s.get(url, timeout=10)
        print(f"状态码: {resp.status_code}")
        print(f"响应头: {dict(resp.cookies)}")
        
        if resp.status_code == 200:
            # 查找CSRF令牌
            csrf_found = False
            for i, line in enumerate(resp.text.split('\n')):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    if start > 6 and end > start:
                        csrf_token = line[start:end]
                        print(f"✅ 在第{i+1}行找到CSRF令牌: {csrf_token[:10]}...")
                        csrf_found = True
                        break
            
            if not csrf_found:
                print("❌ 在HTML中未找到csrfmiddlewaretoken")
                
            # 检查cookies
            if 'csrftoken' in s.cookies:
                print(f"✅ 在cookies中找到CSRF令牌: {s.cookies['csrftoken'][:10]}...")
            else:
                print("❌ cookies中未找到csrftoken")
        else:
            print(f"❌ admin页面访问失败: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ 访问admin页面时发生错误: {str(e)}")
    
    # 方法2: 从登录页面获取
    print("\n📋 方法2: 从登录页面获取")
    try:
        url = urljoin(BASE_URL + '/', 'users/login/')
        print(f"访问URL: {url}")
        resp = s.get(url, timeout=10)
        print(f"状态码: {resp.status_code}")
        
        if resp.status_code == 200:
            # 查找CSRF令牌
            csrf_found = False
            for i, line in enumerate(resp.text.split('\n')):
                if 'csrfmiddlewaretoken' in line and 'value=' in line:
                    start = line.find('value="') + 7
                    end = line.find('"', start)
                    if start > 6 and end > start:
                        csrf_token = line[start:end]
                        print(f"✅ 在第{i+1}行找到CSRF令牌: {csrf_token[:10]}...")
                        csrf_found = True
                        break
            
            if not csrf_found:
                print("❌ 在HTML中未找到csrfmiddlewaretoken")
        else:
            print(f"❌ 登录页面访问失败: {resp.status_code}")
            
    except Exception as e:
        print(f"❌ 访问登录页面时发生错误: {str(e)}")
    
    # 方法3: 尝试POST请求获取
    print("\n📋 方法3: 尝试POST请求获取")
    try:
        url = urljoin(BASE_URL + '/', 'users/login/')
        print(f"POST请求URL: {url}")
        
        # 先发送GET请求获取cookies
        s.get(url, timeout=10)
        
        # 检查cookies
        print(f"当前cookies: {dict(s.cookies)}")
        
        if 'csrftoken' in s.cookies:
            print(f"✅ 通过GET请求获取到CSRF令牌: {s.cookies['csrftoken'][:10]}...")
        else:
            print("❌ 通过GET请求未获取到CSRF令牌")
            
    except Exception as e:
        print(f"❌ POST请求测试时发生错误: {str(e)}")
    
    # 总结
    print("\n📊 总结:")
    if 'csrftoken' in s.cookies:
        csrf_token = s.cookies['csrftoken']
        print(f"✅ 最终获取到CSRF令牌: {csrf_token}")
        print(f"令牌长度: {len(csrf_token)}")
        print(f"可以在请求头中使用: X-CSRFToken: {csrf_token}")
    else:
        print("❌ 未能获取到CSRF令牌")
        print("可能的原因:")
        print("1. Django服务器未运行")
        print("2. CSRF中间件被禁用")
        print("3. 页面不包含CSRF令牌")

if __name__ == "__main__":
    get_csrf_token() 