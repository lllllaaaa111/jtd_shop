#!/usr/bin/env python3
"""
测试wechat_auth模块的接口
包含5个接口：
1. /wechat/login/ - 微信登录（包含用户信息）
2. /wechat/code-login/ - 仅code登录
3. /wechat/user-info/ - 获取微信用户信息
4. /wechat/update-user-info/ - 更新微信用户信息
5. /wechat/access-token/ - 获取access_token
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

class WechatAuthTester:
    def __init__(self):
        self.base = BASE_URL.rstrip('/')
        self.s = requests.Session()
        self.results = []
        self.test_code = "test_code_123456"  # 测试用的code
    
    def test_endpoint(self, method, path, name, data=None, expected_status=200, requires_auth=False):
        """测试单个接口"""
        url = urljoin(self.base + '/', path.lstrip('/'))
        kwargs = {"timeout": 15}
        
        if data:
            kwargs["json"] = data
        
        try:
            resp = self.s.request(method, url, **kwargs)
            status = resp.status_code
            success = status == expected_status
            
            try:
                body = resp.json()
            except Exception:
                body = resp.text[:500]
            
            self.results.append({
                "name": name,
                "method": method,
                "url": path,
                "status": status,
                "expected": expected_status,
                "success": success,
                "response": body
            })
            
            print(f"{name}: {status} ({'OK' if success else 'FAIL'})")
            if not success:
                print(f"  响应: {body}")
                
        except requests.RequestException as e:
            self.results.append({
                "name": name,
                "method": method,
                "url": path,
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "error": str(e)
            })
            print(f"{name}: ERROR {e}")
    
    def run(self):
        """运行所有测试"""
        print("🧪 开始测试wechat_auth接口...")
        
        # 1. 微信登录（包含用户信息）
        login_data = {
            "code": self.test_code,
            "user_info": {
                "nickName": "测试用户",
                "avatarUrl": "https://example.com/avatar.jpg",
                "gender": 1,
                "country": "中国",
                "province": "广东",
                "city": "深圳",
                "language": "zh_CN"
            }
        }
        self.test_endpoint('POST', '/wechat/login/', '微信登录（包含用户信息）', login_data, 200)
        
        # 2. 仅code登录
        code_login_data = {
            "code": self.test_code
        }
        self.test_endpoint('POST', '/wechat/code-login/', '仅code登录', code_login_data, 200)
        
        # 3. 获取微信用户信息（需要认证）
        self.test_endpoint('GET', '/wechat/user-info/', '获取微信用户信息', expected_status=401)
        
        # 4. 更新微信用户信息（需要认证）
        update_data = {
            "nickName": "更新后的昵称",
            "avatarUrl": "https://example.com/new_avatar.jpg",
            "gender": 2,
            "country": "中国",
            "province": "北京",
            "city": "北京",
            "language": "zh_CN"
        }
        self.test_endpoint('POST', '/wechat/update-user-info/', '更新微信用户信息', update_data, 401)
        
        # 5. 获取access_token（公开接口）
        self.test_endpoint('GET', '/wechat/access-token/', '获取access_token', expected_status=200)
        
        # 保存结果
        with open('wechat_auth_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 测试完成，共测试 {len(self.results)} 个接口")
        success_count = sum(1 for r in self.results if r['success'])
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {len(self.results) - success_count}")
        print("📄 结果已保存: wechat_auth_test_results.json")

if __name__ == '__main__':
    WechatAuthTester().run() 