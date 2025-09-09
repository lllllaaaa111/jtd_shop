#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_aes_phone():
    """测试AES解密手机号接口"""
    
    # 测试数据
    test_data = {
        "encryptedDatastr": "bYSFRtwz5tNGWxeBETJ9ViV9wlvcJQ7wv1mRrHKEthIW8kYdzPxsdVSJbJahMsv9RwSBE0a3McAZZKkhuF6htsg1fAX5bWLKt2k38y4bTTKzyjjQd9Rs91gJOF/MeTzApDqHZyw19h0PF3fYmgj+zMZy5kRF5FUnvDoC3QIUro4rlyT8D7IKufEQDByUxoVidkQQR35xU6kq/5eGp+dXVw==",
        "iv": "StShheFpyArOB5BsNyn2Eg==",
        "key": "0b3nSH0w3VGMz53A372w3HQObh0nSH0G"
    }
    
    # 接口URL
    url = "http://localhost:6580/users/aes/phone/"
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print("测试AES解密手机号接口")
    print("=" * 50)
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print("-" * 50)
    
    try:
        # 发送POST请求
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 50)
        
        # 尝试解析响应
        try:
            response_json = response.json()
            print(f"响应JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"响应文本: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_aes_phone() 