#!/usr/bin/env python3
"""
WeChat Mini-Program Login Interface Test Script
测试微信小程序登录相关接口
"""

import requests
import json
import sys
from urllib.parse import urljoin

class WeChatLoginTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.openid = None
        self.session_cookie = None
        
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            url = urljoin(self.base_url, '/users/csrf/token/')
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    self.csrf_token = data['result']['csrf_token']
                    print(f"✅ 获取CSRF令牌成功: {self.csrf_token[:20]}...")
                    return True
            print(f"❌ 获取CSRF令牌失败: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ 获取CSRF令牌异常: {e}")
            return False
    
    def test_wechat_getopenid(self, res_code):
        """测试微信获取openid接口"""
        try:
            url = urljoin(self.base_url, '/users/wechat/getopenid/')
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token,
                'X-Csrftoken': self.csrf_token,
                'Referer': self.base_url + '/'
            }
            
            data = {
                "res_code": res_code,
                "msg": "login"
            }
            
            print(f"🔄 测试微信获取openid接口...")
            print(f"   请求URL: {url}")
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            response = self.session.post(url, json=data, headers=headers)
            
            print(f"   响应状态: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    self.openid = result['result']['openid']
                    self.session_cookie = result['result']['session_key_cookie']
                    print(f"✅ 微信登录成功!")
                    print(f"   OpenID: {self.openid}")
                    print(f"   Session Cookie: {self.session_cookie[:20]}...")
                    print(f"   用户信息: {result['result']['userinfo']}")
                    return True
                else:
                    print(f"❌ 微信登录失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试微信获取openid异常: {e}")
            return False
    
    def test_wechat_session_check(self):
        """测试微信会话检查接口"""
        if not self.openid:
            print("❌ 没有openid，无法测试会话检查")
            return False
            
        try:
            url = urljoin(self.base_url, '/users/wechat/session/')
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token,
                'X-Csrftoken': self.csrf_token,
                'Referer': self.base_url + '/'
            }
            
            data = {
                "openid": self.openid,
                "msg": "check"
            }
            
            print(f"🔄 测试微信会话检查接口...")
            print(f"   请求URL: {url}")
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            response = self.session.post(url, json=data, headers=headers)
            
            print(f"   响应状态: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"✅ 会话检查成功!")
                    print(f"   会话状态: {result['result']}")
                    return True
                else:
                    print(f"❌ 会话检查失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试微信会话检查异常: {e}")
            return False
    
    def test_wechat_session_renew(self):
        """测试微信会话续期接口"""
        if not self.openid:
            print("❌ 没有openid，无法测试会话续期")
            return False
            
        try:
            url = urljoin(self.base_url, '/users/wechat/session/')
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token,
                'X-Csrftoken': self.csrf_token,
                'Referer': self.base_url + '/'
            }
            
            data = {
                "openid": self.openid,
                "msg": "renew"
            }
            
            print(f"🔄 测试微信会话续期接口...")
            print(f"   请求URL: {url}")
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            response = self.session.post(url, json=data, headers=headers)
            
            print(f"   响应状态: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"✅ 会话续期成功!")
                    print(f"   续期结果: {result['result']}")
                    return True
                else:
                    print(f"❌ 会话续期失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试微信会话续期异常: {e}")
            return False
    
    def test_wechat_session_logout(self):
        """测试微信会话登出接口"""
        if not self.openid:
            print("❌ 没有openid，无法测试会话登出")
            return False
            
        try:
            url = urljoin(self.base_url, '/users/wechat/session/')
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.csrf_token,
                'X-Csrftoken': self.csrf_token,
                'Referer': self.base_url + '/'
            }
            
            data = {
                "openid": self.openid,
                "msg": "logout"
            }
            
            print(f"🔄 测试微信会话登出接口...")
            print(f"   请求URL: {url}")
            print(f"   请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            response = self.session.post(url, json=data, headers=headers)
            
            print(f"   响应状态: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"✅ 会话登出成功!")
                    print(f"   登出结果: {result['result']}")
                    return True
                else:
                    print(f"❌ 会话登出失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 测试微信会话登出异常: {e}")
            return False

def main():
    print("🚀 开始测试微信小程序登录接口")
    print("=" * 50)
    
    # 从命令行参数获取res_code，如果没有则使用默认值
    res_code = "0b3RM1000xiVVU1yQU000VdnUb1RM10B"
    if len(sys.argv) > 1:
        res_code = sys.argv[1]
    
    print(f"📱 使用res_code: {res_code}")
    print()
    
    tester = WeChatLoginTester()
    
    # 1. 获取CSRF令牌
    print("1️⃣ 获取CSRF令牌")
    if not tester.get_csrf_token():
        print("❌ 无法获取CSRF令牌，测试终止")
        return
    print()
    
    # 2. 测试微信获取openid
    print("2️⃣ 测试微信获取openid")
    if not tester.test_wechat_getopenid(res_code):
        print("❌ 微信获取openid失败，测试终止")
        return
    print()
    
    # 3. 测试会话检查
    print("3️⃣ 测试会话检查")
    tester.test_wechat_session_check()
    print()
    
    # 4. 测试会话续期
    print("4️⃣ 测试会话续期")
    tester.test_wechat_session_renew()
    print()
    
    # 5. 再次测试会话检查
    print("5️⃣ 再次测试会话检查")
    tester.test_wechat_session_check()
    print()
    
    # 6. 测试会话登出
    print("6️⃣ 测试会话登出")
    tester.test_wechat_session_logout()
    print()
    
    # 7. 最后测试会话检查（应该显示已登出）
    print("7️⃣ 最后测试会话检查（应该显示已登出）")
    tester.test_wechat_session_check()
    print()
    
    print("🎉 微信小程序登录接口测试完成!")

if __name__ == "__main__":
    main()
