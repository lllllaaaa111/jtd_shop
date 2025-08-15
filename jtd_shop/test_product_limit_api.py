#!/usr/bin/env python3
"""
测试商品列表接口的数量参数功能
"""
import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
USERNAME = "root"
PASSWORD = "Gg666666"

class ProductLimitTester:
    def __init__(self):
        self.base = BASE_URL.rstrip('/')
        self.s = requests.Session()
        self.results = []
        self.is_session_auth = False
        self.csrf_token = None
    
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            url = urljoin(self.base + '/', 'admin/')
            resp = self.s.get(url, timeout=10)
            if resp.status_code == 200 and 'csrftoken' in self.s.cookies:
                self.csrf_token = self.s.cookies['csrftoken']
                print(f"✅ 获取到CSRF令牌: {self.csrf_token[:10]}...")
                return True
            return False
        except Exception as e:
            print(f"❌ 获取CSRF令牌失败: {str(e)}")
            return False
    
    def login_session(self):
        """Session登录"""
        try:
            url = urljoin(self.base + '/', 'users/login/')
            if not self.csrf_token:
                self.get_csrf_token()
            
            login_data = {"username": USERNAME, "password": PASSWORD}
            headers = {'Content-Type': 'application/json'}
            
            if self.csrf_token:
                headers['X-CSRFToken'] = self.csrf_token
            
            resp = self.s.post(url, json=login_data, headers=headers, timeout=10)
            if resp.status_code == 200 and isinstance(resp.json(), dict) and resp.json().get('code') == 200:
                self.is_session_auth = True
                print("✅ Session登录成功")
                
                # 重新获取CSRF令牌
                self.get_csrf_token()
                return True
            else:
                print(f"⚠️ Session登录失败: {resp.status_code}")
                return False
        except Exception as e:
            print(f"⚠️ Session登录异常: {str(e)}")
            return False
    
    def test_api_call(self, method: str, path: str, name: str, expected_status=200, params=None):
        """测试API调用"""
        url = urljoin(self.base + '/', path.lstrip('/'))
        kwargs = {"timeout": 15}
        
        if params:
            kwargs["params"] = params
        
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
                "params": params,
                "status": status,
                "expected": expected_status,
                "success": success,
                "response": body
            })
            
            print(f"{name}: {status} ({'OK' if success else 'FAIL'})")
            
            # 显示详细信息
            if success and method == 'GET' and 'result' in body:
                if 'products' in body['result']:
                    products_count = len(body['result']['products'])
                    total_count = body['result'].get('total_count', products_count)
                    limit = body['result'].get('limit')
                    print(f"  📦 返回商品数: {products_count}, 总数: {total_count}, 限制: {limit}")
                elif isinstance(body['result'], list):
                    print(f"  📦 项目数量: {len(body['result'])}")
            
            return success
            
        except requests.RequestException as e:
            self.results.append({
                "name": name,
                "method": method,
                "url": path,
                "params": params,
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "error": str(e)
            })
            print(f"{name}: ERROR {e}")
            return False
    
    def run_tests(self):
        """运行所有测试"""
        print("🚀 开始测试商品列表数量参数功能")
        print("=" * 60)
        
        # 1. 获取CSRF令牌
        print("🔑 获取CSRF令牌...")
        self.get_csrf_token()
        
        # 2. Session登录
        print("🔐 Session登录...")
        self.login_session()
        
        if not self.is_session_auth:
            print("❌ Session登录失败，无法继续测试")
            return
        
        # 3. 测试基础商品列表（无限制）
        print("\n📋 测试基础商品列表...")
        self.test_api_call('GET', '/products/list/', '获取所有商品')
        
        # 4. 测试有效的数量限制
        print("\n📋 测试有效的数量限制...")
        self.test_api_call('GET', '/products/list/', '限制1个商品', params={'limit': 1})
        self.test_api_call('GET', '/products/list/', '限制5个商品', params={'limit': 5})
        self.test_api_call('GET', '/products/list/', '限制10个商品', params={'limit': 10})
        self.test_api_call('GET', '/products/list/', '限制100个商品', params={'limit': 100})
        
        # 5. 测试无效的数量参数
        print("\n📋 测试无效的数量参数...")
        self.test_api_call('GET', '/products/list/', '限制0个商品', expected_status=400, params={'limit': 0})
        self.test_api_call('GET', '/products/list/', '限制负数', expected_status=400, params={'limit': -1})
        self.test_api_call('GET', '/products/list/', '无效参数-字符串', expected_status=400, params={'limit': 'abc'})
        self.test_api_call('GET', '/products/list/', '无效参数-小数', expected_status=400, params={'limit': 3.14})
        self.test_api_call('GET', '/products/list/', '无效参数-空字符串', expected_status=400, params={'limit': ''})
        
        # 6. 测试边界情况
        print("\n📋 测试边界情况...")
        self.test_api_call('GET', '/products/list/', '极大数值', params={'limit': 999999})
        self.test_api_call('GET', '/products/list/', '参数名错误', params={'limits': 5})
        
        # 7. 测试其他商品相关接口
        print("\n📋 测试其他商品接口...")
        self.test_api_call('GET', '/products/category/list/', '获取商品分类列表')
        self.test_api_call('GET', '/products/detail/1/', '获取商品详情')
        
        # 8. 保存测试结果
        with open('product_limit_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 9. 统计结果
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result['success'])
        
        print("\n" + "=" * 60)
        print("📊 测试结果统计")
        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"失败数: {total_tests - successful_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        print("📄 详细结果已保存: product_limit_test_results.json")
        
        # 10. 功能验证总结
        print("\n🔍 功能验证总结:")
        limit_tests = [r for r in self.results if 'limit' in str(r.get('params', {}))]
        valid_limit_tests = [r for r in limit_tests if r['success'] and r['status'] == 200]
        invalid_limit_tests = [r for r in limit_tests if r['success'] and r['status'] == 400]
        
        print(f"✅ 有效数量参数测试: {len(valid_limit_tests)}/{len([r for r in limit_tests if r['expected'] == 200])}")
        print(f"✅ 无效数量参数测试: {len(invalid_limit_tests)}/{len([r for r in limit_tests if r['expected'] == 400])}")

def main():
    tester = ProductLimitTester()
    tester.run_tests()

if __name__ == "__main__":
    main() 