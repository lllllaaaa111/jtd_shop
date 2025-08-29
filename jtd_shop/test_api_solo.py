#!/usr/bin/env python3
"""
使用root/Gg666666对现有接口进行测试。
优先使用Session登录(/users/login/)，若失败，回退到HTTP Basic认证。
覆盖API_DOCUMENTATION.md中的接口列表，保存结果到 api_test_results_root.json。
"""
import requests
import json
from urllib.parse import urljoin

# BASE_URL = "http://localhost:6580"
# BASE_URL = "https://jtd.wxdnet.cn:8080"
BASE_URL = "https://jtd.wxdnet.cn:8080"
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
                # 关键：Referer 需与可信域一致
                kwargs['headers']['Referer'] = self.base + '/'
            
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
            return resp
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
            return None

    def post_multipart(self, path: str, name: str, form_data: dict, files=None, expected_status=201):
        url = urljoin(self.base + '/', path.lstrip('/'))
        headers = {}
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
            headers['X-Csrftoken'] = self.csrf_token
        try:
            resp = self.s.post(url, data=form_data, files=files, headers=headers, timeout=20)
            status = resp.status_code
            success = status == expected_status
            try:
                body = resp.json()
            except Exception:
                body = resp.text[:500]
            self.results.append({
                "name": name,
                "method": "POST",
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
                "method": "POST",
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
        
        # CSRF认证接口测试
        print("🔒 测试CSRF认证接口...")
        self.call('GET', '/users/csrf/info/', '获取CSRF信息')
        self.call('GET', '/users/csrf/token/', '获取CSRF令牌')
        
        # 测试CSRF令牌验证
        if self.csrf_token:
            self.call('POST', '/users/csrf/validate/', '验证CSRF令牌', expected_status=200, json_data={})
        
        # 商品分类接口测试
        print("🛍️ 测试商品分类接口...")
        self.call('GET', '/products/category/list/', '获取商品分类列表')
        self.call('GET', '/products/list/', '获取商品列表')
        self.call('GET', '/products/list/?limit=5', '获取商品列表-限制5个')
        self.call('GET', '/products/list/?limit=10', '获取商品列表-限制10个')
        self.call('GET', '/products/list/?limit=1', '获取商品列表-限制1个')
        self.call('GET', '/products/list/?limit=0', '获取商品列表-限制0个', expected_status=400)
        self.call('GET', '/products/list/?limit=abc', '获取商品列表-无效参数', expected_status=400)
        self.call('GET', '/products/detail/1/', '获取商品详情')
        
        # 测试按分类名称模糊匹配获取商品
        self.call('GET', '/products/by-category/?category_name=电子', '按分类模糊匹配-电子')
        self.call('GET', '/products/by-category/?category_name=电子&limit=3', '按分类模糊匹配-电子-限制3个')
        self.call('GET', '/products/by-category/?category_name=服装', '按分类模糊匹配-服装')
        self.call('GET', '/products/by-category/?category_name=服装&limit=5', '按分类模糊匹配-服装-限制5个')
        self.call('GET', '/products/by-category/?category_name=零', '按分类模糊匹配-零')
        self.call('GET', '/products/by-category/?category_name=零&limit=1', '按分类模糊匹配-零-限制1个')
        
        # 测试按分类名称精确匹配获取商品
        self.call('GET', '/products/by-category/电子产品/', '按分类精确匹配-电子产品')
        self.call('GET', '/products/by-category/电子产品/?limit=2', '按分类精确匹配-电子产品-限制2个')
        self.call('GET', '/products/by-category/服装鞋帽/', '按分类精确匹配-服装鞋帽')
        self.call('GET', '/products/by-category/服装鞋帽/?limit=10', '按分类精确匹配-服装鞋帽-限制10个')
        self.call('GET', '/products/by-category/不存在的分类/', '按分类精确匹配-不存在分类', expected_status=404)
        
        # 测试无效的limit参数
        self.call('GET', '/products/by-category/?category_name=电子&limit=0', '按分类模糊匹配-无效limit-0', expected_status=400)
        self.call('GET', '/products/by-category/?category_name=电子&limit=abc', '按分类模糊匹配-无效limit-字符串', expected_status=400)
        self.call('GET', '/products/by-category/电子产品/?limit=-1', '按分类精确匹配-无效limit-负数', expected_status=400)
        
        # 测试空参数
        self.call('GET', '/products/by-category/?category_name=', '按分类模糊匹配-空参数', expected_status=400)
        
        # 新增商品接口（multipart/form-data）
        print("🧪 测试新增商品接口（multipart/form-data）...")
        product_form = {
            'name': '自动化测试商品',
            'price': '9.99',
            'category_name': '电子产品',
            'description': '由test_api_solo创建的商品',
            'stock': '5',
            'manufacturer': 'TestCo'
        }
        self.post_multipart('/products/create/', '新增商品-最小必填+可选', form_data=product_form, files=None, expected_status=201)
        
        # 使用指定的图片文件进行测试
        try:
            image_path = "/mnt/c/Users/Administrator.DESKTOP-DOMHQ5D/Desktop/金天得小程序/产品图片参考/test_1.jpg"
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                files = [('images', ('test_1.jpg', img_data, 'image/jpeg'))]
                product_form2 = {
                    'name': '自动化测试商品-带图片',
                    'price': '19.99',
                    'category_name': '电子产品',
                    'description': '含图片的商品，使用指定图片文件',
                    'stock': '10',
                    'manufacturer': 'TestCo'
                }
                self.post_multipart('/products/create/', '新增商品-含指定图片', form_data=product_form2, files=files, expected_status=201)
        except Exception as e:
            print(f"图片上传测试失败: {e}")
            # 回退到内置图片测试
            try:
                import base64
                png_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/afS7gAAAABJRU5ErkJggg=='
                png_bytes = base64.b64decode(png_b64)
                files = [('images', ('test.png', png_bytes, 'image/png'))]
                product_form2 = {
                    'name': '自动化测试商品-带内置图片',
                    'price': '19.99',
                    'category_name': '电子产品',
                    'description': '含内置图片的商品',
                }
                self.post_multipart('/products/create/', '新增商品-含内置图片', form_data=product_form2, files=files, expected_status=201)
            except Exception as e2:
                print(f"内置图片测试也失败: {e2}")

        # 订单接口测试
        print("🧾 测试订单接口...")
        # 先尝试创建订单（如果购物车为空，可能返回400）
        create_payload = {
            'delivery_address': '上海市徐汇区XX路1号',
            'recipient_name': '张三',
            'recipient_phone': '13800000000',
            'payment_method': 'wechat'
        }
        resp_create = self.call('POST', '/orders/create/', '创建订单', expected_status=200, json_data=create_payload)
        internal_no = None
        try:
            if resp_create is not None and resp_create.status_code == 200:
                data = resp_create.json()
                if isinstance(data, dict) and isinstance(data.get('result'), dict):
                    internal_no = data['result'].get('internal_order_number')
        except Exception:
            pass

        # 如创建失败或未返回内部订单号，则查询订单列表以获取一个可用订单
        resp_list = self.call('GET', '/orders/list/', '订单列表')
        try:
            if not internal_no and resp_list is not None:
                data = resp_list.json()
                if isinstance(data, dict) and isinstance(data.get('result'), list) and data['result']:
                    first = data['result'][0]
                    internal_no = first.get('internal_order_number') or None
        except Exception:
            pass

        # 若拿到内部订单号，测试更新状态为已支付
        if internal_no:
            update_payload = {
                'internal_order_number': internal_no,
                'status': 'paid',
                'payment_method': 'wechat'
            }
            self.call('POST', '/orders/update-status/', '更新订单状态为已支付', expected_status=200, json_data=update_payload)
        else:
            # 记录未能获得内部订单号的情况
            self.results.append({
                'name': '更新订单状态为已支付',
                'method': 'POST',
                'url': '/orders/update-status/',
                'status': 'SKIPPED',
                'expected': 200,
                'success': False,
                'response': '未找到可用于更新的内部订单号（创建失败且订单列表为空）'
            })
        
        with open('api_test_results_solo.json','w',encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print('📄 结果已保存: api_test_results_solo.json')

if __name__ == '__main__':
    RootAPITester().run() 