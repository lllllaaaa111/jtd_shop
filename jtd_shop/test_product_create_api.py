#!/usr/bin/env python3
"""
测试商品创建接口，使用指定的图片文件
"""
import requests
import json
from urllib.parse import urljoin
import os

BASE_URL = "http://localhost:8000"
USERNAME = "root"
PASSWORD = "Gg666666"
IMAGE_PATH = "/mnt/c/Users/Administrator.DESKTOP-DOMHQ5D/Desktop/金天得小程序/产品图片参考/test_1.jpg"

class ProductCreateTester:
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
    
    def test_product_creation(self, name: str, form_data: dict, files=None, expected_status=201):
        """测试商品创建"""
        url = urljoin(self.base + '/', 'products/create/')
        headers = {}
        
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
            headers['X-Csrftoken'] = self.csrf_token
        
        try:
            resp = self.s.post(url, data=form_data, files=files, headers=headers, timeout=30)
            status = resp.status_code
            success = status == expected_status
            
            try:
                body = resp.json()
            except Exception:
                body = resp.text[:500]
            
            self.results.append({
                "name": name,
                "method": "POST",
                "url": "/products/create/",
                "form_data": form_data,
                "files": "有图片" if files else "无图片",
                "status": status,
                "expected": expected_status,
                "success": success,
                "response": body
            })
            
            print(f"{name}: {status} ({'OK' if success else 'FAIL'})")
            
            # 显示详细信息
            if success and 'result' in body:
                result = body['result']
                print(f"  🆔 商品ID: {result.get('id')}")
                print(f"  📦 商品名称: {result.get('name')}")
                print(f"  💰 价格: {result.get('price')}")
                print(f"  🏷️ 分类: {result.get('category_name')}")
                if 'images' in result:
                    print(f"  🖼️ 图片数量: {len(result['images'])}")
                    for i, img in enumerate(result['images']):
                        print(f"    图片{i+1}: {img.get('is_primary', False) and '主图' or '次图'} - {img.get('image_url', '')[:50]}...")
            
            return success
            
        except requests.RequestException as e:
            self.results.append({
                "name": name,
                "method": "POST",
                "url": "/products/create/",
                "form_data": form_data,
                "files": "有图片" if files else "无图片",
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "error": str(e)
            })
            print(f"{name}: ERROR {e}")
            return False
    
    def run_tests(self):
        """运行所有测试"""
        print("🚀 开始测试商品创建接口")
        print("=" * 60)
        print(f"📁 使用图片文件: {IMAGE_PATH}")
        
        # 检查图片文件是否存在
        if not os.path.exists(IMAGE_PATH):
            print(f"❌ 图片文件不存在: {IMAGE_PATH}")
            return
        
        print(f"✅ 图片文件存在，大小: {os.path.getsize(IMAGE_PATH)} 字节")
        
        # 1. 获取CSRF令牌
        print("\n🔑 获取CSRF令牌...")
        self.get_csrf_token()
        
        # 2. Session登录
        print("🔐 Session登录...")
        self.login_session()
        
        if not self.is_session_auth:
            print("❌ Session登录失败，无法继续测试")
            return
        
        # 3. 测试基础商品创建（无图片）
        print("\n📋 测试基础商品创建...")
        basic_form = {
            'name': '基础测试商品',
            'price': '29.99',
            'category_name': '电子产品',
            'description': '这是一个基础测试商品，不包含图片',
            'stock': '15',
            'manufacturer': '基础测试厂商'
        }
        self.test_product_creation('创建基础商品-无图片', basic_form, expected_status=201)
        
        # 4. 测试带图片的商品创建
        print("\n📋 测试带图片的商品创建...")
        try:
            with open(IMAGE_PATH, 'rb') as img_file:
                img_data = img_file.read()
                files = [('images', ('test_1.jpg', img_data, 'image/jpeg'))]
                
                image_form = {
                    'name': '图片测试商品',
                    'price': '99.99',
                    'category_name': '电子产品',
                    'description': '这是一个包含图片的测试商品',
                    'stock': '20',
                    'manufacturer': '图片测试厂商',
                    'original_price': '129.99'
                }
                
                self.test_product_creation('创建商品-含指定图片', image_form, files, expected_status=201)
        except Exception as e:
            print(f"❌ 图片文件读取失败: {e}")
        
        # 5. 测试必填字段验证
        print("\n📋 测试必填字段验证...")
        
        # 缺少商品名称
        missing_name_form = {
            'price': '29.99',
            'category_name': '电子产品'
        }
        self.test_product_creation('创建商品-缺少商品名称', missing_name_form, expected_status=400)
        
        # 缺少价格
        missing_price_form = {
            'name': '测试商品',
            'category_name': '电子产品'
        }
        self.test_product_creation('创建商品-缺少价格', missing_price_form, expected_status=400)
        
        # 缺少分类
        missing_category_form = {
            'name': '测试商品',
            'price': '29.99'
        }
        self.test_product_creation('创建商品-缺少分类', missing_category_form, expected_status=400)
        
        # 6. 测试数据格式验证
        print("\n📋 测试数据格式验证...")
        
        # 无效价格
        invalid_price_form = {
            'name': '测试商品',
            'price': 'abc',
            'category_name': '电子产品'
        }
        self.test_product_creation('创建商品-无效价格', invalid_price_form, expected_status=400)
        
        # 负数价格
        negative_price_form = {
            'name': '测试商品',
            'price': '-10',
            'category_name': '电子产品'
        }
        self.test_product_creation('创建商品-负数价格', negative_price_form, expected_status=400)
        
        # 7. 保存测试结果
        with open('product_create_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 8. 统计结果
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results if result['success'])
        
        print("\n" + "=" * 60)
        print("📊 测试结果统计")
        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"失败数: {total_tests - successful_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        print("📄 详细结果已保存: product_create_test_results.json")
        
        # 9. 功能验证总结
        print("\n🔍 功能验证总结:")
        create_tests = [r for r in self.results if '创建商品' in r['name'] and r['success']]
        validation_tests = [r for r in self.results if '缺少' in r['name'] or '无效' in r['name'] or '负数' in r['name']]
        successful_validation = [r for r in validation_tests if r['success']]
        
        print(f"✅ 商品创建成功: {len(create_tests)}")
        print(f"✅ 字段验证正常: {len(successful_validation)}/{len(validation_tests)}")

def main():
    tester = ProductCreateTester()
    tester.run_tests()

if __name__ == "__main__":
    main() 