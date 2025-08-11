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
USERNAME = "root"
PASSWORD = "Gg666666"

class RootAPITester:
    def __init__(self):
        self.base = BASE_URL.rstrip('/')
        self.s = requests.Session()
        self.results = []
        self.is_session_auth = False
        self.basic_auth = (USERNAME, PASSWORD)
        self.csrf_token = None
    
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            # 访问一个页面来获取CSRF令牌
            url = urljoin(self.base + '/', 'admin/')
            resp = self.s.get(url, timeout=10)
            if resp.status_code == 200:
                # 从响应中提取CSRF令牌
                for line in resp.text.split('\n'):
                    if 'csrfmiddlewaretoken' in line and 'value=' in line:
                        # 提取CSRF令牌值
                        start = line.find('value="') + 7
                        end = line.find('"', start)
                        if start > 6 and end > start:
                            self.csrf_token = line[start:end]
                            print(f"✅ 获取到CSRF令牌: {self.csrf_token[:10]}...")
                            return True
                
                # 如果没找到，尝试从cookies中获取
                if 'csrftoken' in self.s.cookies:
                    self.csrf_token = self.s.cookies['csrftoken']
                    print(f"✅ 从cookies获取到CSRF令牌: {self.csrf_token[:10]}...")
                    return True
                    
            print("⚠️ 无法从admin页面获取CSRF令牌，尝试其他方法")
            
            # 尝试从登录页面获取
            url = urljoin(self.base + '/', 'users/login/')
            resp = self.s.get(url, timeout=10)
            if resp.status_code == 200:
                for line in resp.text.split('\n'):
                    if 'csrfmiddlewaretoken' in line and 'value=' in line:
                        start = line.find('value="') + 7
                        end = line.find('"', start)
                        if start > 6 and end > start:
                            self.csrf_token = line[start:end]
                            print(f"✅ 从登录页面获取到CSRF令牌: {self.csrf_token[:10]}...")
                            return True
            
            print("❌ 无法获取CSRF令牌")
            return False
            
        except Exception as e:
            print(f"❌ 获取CSRF令牌时发生错误: {str(e)}")
            return False
    
    def login_session(self):
        try:
            url = urljoin(self.base + '/', 'users/login/')
            # 先获取CSRF令牌
            if not self.csrf_token:
                self.get_csrf_token()
            
            # 准备登录数据
            login_data = {"username": USERNAME, "password": PASSWORD}
            headers = {'Content-Type': 'application/json'}
            
            # 如果有CSRF令牌，添加到请求头
            if self.csrf_token:
                headers['X-CSRFToken'] = self.csrf_token
            
            resp = self.s.post(url, json=login_data, headers=headers, timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict) and resp.json().get('code') == 200:
                self.is_session_auth = True
                print("✅ Session登录成功")
                
                # 登录成功后重新获取CSRF令牌
                print("🔄 登录成功后重新获取CSRF令牌...")
                self.get_csrf_token()
                
                return True
            else:
                print(f"⚠️ Session登录失败: {resp.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Session登录异常: {str(e)}")
            return False
    
    def call(self, method: str, path: str, name: str, expected_status=200, json_data=None):
        url = urljoin(self.base + '/', path.lstrip('/'))
        kwargs = {"timeout": 15}
        
        # 处理POST请求的JSON数据和CSRF令牌
        if method == 'POST':
            if json_data:
                kwargs["json"] = json_data
            
            # 添加CSRF令牌到请求头
            if self.csrf_token:
                if 'headers' not in kwargs:
                    kwargs['headers'] = {}
                kwargs['headers']['X-CSRFToken'] = self.csrf_token
                kwargs['headers']['X-Csrftoken'] = self.csrf_token  # Django也接受这个格式
                kwargs['headers']['Content-Type'] = 'application/json'
            
            # 特殊处理用户注册
            if path.endswith('/users/register/'):
                if not json_data:
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
        # 获取CSRF令牌
        print("🔑 正在获取CSRF令牌...")
        self.get_csrf_token()
        
        # 登录尝试
        print("🔐 正在尝试Session登录...")
        self.login_session()
        
        # 新建订单接口测试
        order_data = {
            "delivery_address": "北京市朝阳区某某街道123号",
            "recipient_name": "张三",
            "recipient_phone": "13800138000",
            "shipping_address": "上海市浦东新区某某仓库",
            "notes": "请尽快发货",
            "payment_method": "alipay"
        }
        self.call('POST', '/orders/create/', '新建订单-完整数据', expected_status=200, json_data=order_data)

        self.call('GET', '/orders/list/', '订单列表')
        self.call('GET', '/orders/detail/1/', '订单详情')
        self.call('GET', '/orders/cart/list/', '购物车列表')
        
        # 测试缺少必填字段的情况
        incomplete_order_data = {
            "delivery_address": "北京市朝阳区某某街道123号"
            # 缺少 recipient_name 和 recipient_phone
        }
        self.call('POST', '/orders/create/', '新建订单-缺少必填字段', expected_status=400, json_data=incomplete_order_data)
        
        # 测试空购物车的情况（如果购物车为空）
        empty_cart_order_data = {
            "delivery_address": "北京市朝阳区某某街道123号",
            "recipient_name": "李四",
            "recipient_phone": "13900139000"
        }
        self.call('POST', '/orders/create/', '新建订单-空购物车', expected_status=400, json_data=empty_cart_order_data)
        
        with open('api_test_results_solo.json','w',encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print('📄 结果已保存: api_test_results_solo.json')

if __name__ == '__main__':
    RootAPITester().run() 