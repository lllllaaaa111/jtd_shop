#!/usr/bin/env python3
"""
使用root/Gg666666对现有接口进行测试。
优先使用Session登录(/users/login/)，若失败，回退到HTTP Basic认证。
覆盖API_DOCUMENTATION.md中的接口列表，保存结果到 api_test_results_root.json。
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "Gg666666"

class RootAPITester:
    def __init__(self):
        self.base = BASE_URL.rstrip('/')
        self.s = requests.Session()
        self.results = []
        self.is_session_auth = False
        self.basic_auth = (USERNAME, PASSWORD)
    
    def login_session(self):
        try:
            url = urljoin(self.base + '/', 'users/login/')
            resp = self.s.post(url, json={"username": USERNAME, "password": PASSWORD}, timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict) and resp.json().get('code') == 200:
                self.is_session_auth = True
                return True
        except Exception:
            pass
        return False
    
    def call(self, method: str, path: str, name: str, expected_status=200):
        url = urljoin(self.base + '/', path.lstrip('/'))
        kwargs = {"timeout": 15}
        # 对POST默认不带body，只有创建用户时带
        if method == 'POST' and path.endswith('/users/register/'):
            kwargs["json"] = {
                "username": "root_api_user",
                "email": "root_api_user@example.com",
                "password": "testpass123",
                "password_confirm": "testpass123"
            }
        
        try:
            # 先用session（如已登录）
            if self.is_session_auth:
                resp = self.s.request(method, url, **kwargs)
            else:
                # 用Basic认证兜底（DRF配置支持BasicAuthentication）
                resp = self.s.request(method, url, auth=self.basic_auth, **kwargs)
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
        # 登录尝试
        self.login_session()
        
        # smart
        self.call('GET', '/smart/index/', '首页接口')
        self.call('GET', '/smart/films/', '电影列表')
        self.call('GET', '/smart/random/', '随机数据')
        
        # users
        self.call('GET', '/users/list/', '用户列表')
        self.call('GET', '/users/detail/1/', '用户详情')
        self.call('POST', '/users/register/', '创建用户', expected_status=201)
        self.call('GET', '/users/avatar/', '获取用户头像')
        self.call('GET', '/users/avatar/list/', '头像列表')
        
        # products
        self.call('GET', '/products/category/list/', '分类列表')
        self.call('GET', '/products/list/', '商品列表')
        self.call('GET', '/products/detail/1/', '商品详情')
        
        # orders
        self.call('GET', '/orders/list/', '订单列表')
        self.call('GET', '/orders/detail/1/', '订单详情')
        self.call('GET', '/orders/cart/list/', '购物车列表')
        
        # content
        self.call('GET', '/content/welcome/', '欢迎页面')
        self.call('GET', '/content/welcome/list/', '欢迎图片列表')
        self.call('GET', '/content/banner/list/', '轮播图列表')
        self.call('GET', '/content/article/list/', '文章列表')
        self.call('GET', '/content/article/detail/1/', '文章详情')
        self.call('GET', '/content/notice/list/', '系统公告列表')
        
        # system
        self.call('GET', '/system/config/list/', '系统配置列表')
        self.call('GET', '/system/log/list/', '操作日志列表')
        self.call('GET', '/system/file/list/', '文件上传记录')
        self.call('GET', '/system/backup/list/', '数据备份列表')
        
        # admin
        self.call('GET', '/admin/', 'Django管理后台', expected_status=200)
        
        with open('api_test_results_root.json','w',encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print('📄 结果已保存: api_test_results_root.json')

if __name__ == '__main__':
    RootAPITester().run() 