#!/usr/bin/env python
"""
测试签名串生成接口
"""
import requests
import json
import time

class SignatureStringTester:
    def __init__(self):
        self.base_url = "https://jtd.wxdnet.cn:8080"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Referer': self.base_url + '/'
        })
    
    def test_generate_signature_string(self):
        """测试生成签名串接口"""
        url = f"{self.base_url}/system/signature/generate/"
        
        # 测试数据
        test_data = {
            "method": "POST",
            "url_path": "/v3/pay/transactions/jsapi",
            "timestamp": int(time.time()),
            "nonce_str": "test_nonce_string_12345",
            "body": json.dumps({
                "appid": "wx1234567890abcdef",
                "mchid": "1234567890",
                "description": "测试商品",
                "out_trade_no": "TEST" + str(int(time.time())),
                "notify_url": "https://example.com/notify",
                "amount": {
                    "total": 100,
                    "currency": "CNY"
                },
                "payer": {
                    "openid": "oUpF8uMuAJO_M2pxb1Q9zNjWeS6o"
                }
            })
        }
        
        print("🔍 测试签名串生成接口...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        try:
            response = self.session.post(url, json=test_data)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 请求成功!")
                print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 验证返回的数据结构
                if result.get('code') == 200 and result.get('result'):
                    signature_data = result['result']
                    required_fields = ['signature_string', 'method', 'url_path', 'timestamp', 'nonce_str', 'body']
                    
                    missing_fields = [field for field in required_fields if field not in signature_data]
                    if missing_fields:
                        print(f"❌ 缺少必要字段: {missing_fields}")
                    else:
                        print("✅ 签名串生成成功，包含所有必要字段")
                        print(f"签名串: {repr(signature_data['signature_string'])}")
                        print(f"签名串长度: {len(signature_data['signature_string'])}")
                        
                        # 验证签名串格式
                        signature_lines = signature_data['signature_string'].split('\n')
                        if len(signature_lines) == 6:  # 5行内容 + 1个空行（最后一行以\n结尾）
                            print("✅ 签名串格式正确：5行内容，每行以\\n结尾")
                            for i, line in enumerate(signature_lines[:-1]):  # 排除最后的空行
                                print(f"   第{i+1}行: {repr(line)}")
                        else:
                            print(f"❌ 签名串格式错误：期望6行，实际{len(signature_lines)}行")
                else:
                    print(f"❌ 响应格式错误: {result}")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    def test_different_methods(self):
        """测试不同的HTTP方法"""
        url = f"{self.base_url}/system/signature/generate/"
        
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        print("\n🔍 测试不同的HTTP方法...")
        
        for method in methods:
            test_data = {
                "method": method,
                "url_path": "/v3/test",
                "timestamp": int(time.time()),
                "nonce_str": f"nonce_{method}_{int(time.time())}",
                "body": '{"test": "data"}' if method in ["POST", "PUT"] else ""
            }
            
            print(f"\n测试方法: {method}")
            
            try:
                response = self.session.post(url, json=test_data)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        signature_data = result['result']
                        print(f"✅ {method} 方法签名串生成成功")
                        print(f"   签名串: {repr(signature_data['signature_string'])[:50]}...")
                        print(f"   行数: {len(signature_data['signature_string'].split(chr(10)))}")
                    else:
                        print(f"❌ {method} 方法失败: {result.get('msg', '未知错误')}")
                else:
                    print(f"❌ {method} 方法请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {method} 方法异常: {e}")
    
    def test_edge_cases(self):
        """测试边界情况"""
        url = f"{self.base_url}/system/signature/generate/"
        
        print("\n🔍 测试边界情况...")
        
        # 测试空参数
        test_cases = [
            {
                "name": "空参数",
                "data": {}
            },
            {
                "name": "包含换行符的body",
                "data": {
                    "method": "POST",
                    "url_path": "/v3/test",
                    "timestamp": int(time.time()),
                    "nonce_str": "test_nonce",
                    "body": "line1\nline2\nline3"
                }
            },
            {
                "name": "特殊字符",
                "data": {
                    "method": "POST",
                    "url_path": "/v3/test?param=value&param2=value2",
                    "timestamp": int(time.time()),
                    "nonce_str": "test_nonce_!@#$%",
                    "body": '{"key": "value", "special": "!@#$%^&*()"}'
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n测试: {test_case['name']}")
            
            try:
                response = self.session.post(url, json=test_case['data'])
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        signature_data = result['result']
                        print(f"✅ 成功生成签名串")
                        print(f"   签名串长度: {len(signature_data['signature_string'])}")
                        print(f"   行数: {len(signature_data['signature_string'].split(chr(10)))}")
                    else:
                        print(f"❌ 失败: {result.get('msg', '未知错误')}")
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 异常: {e}")

def main():
    tester = SignatureStringTester()
    
    print("🚀 开始测试签名串生成接口")
    print("=" * 50)
    
    # 测试基本功能
    tester.test_generate_signature_string()
    
    # 测试不同HTTP方法
    tester.test_different_methods()
    
    # 测试边界情况
    tester.test_edge_cases()
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")

if __name__ == "__main__":
    main() 