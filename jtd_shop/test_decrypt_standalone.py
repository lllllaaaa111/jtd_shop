#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
from Crypto.Cipher import AES

def test_aes_decrypt():
    """独立测试AES解密逻辑"""
    
    # 测试参数
    key_b64 = '0b3nSH0w3VGMz53A372w3HQObh0nSH0G'
    iv_b64 = 'StShheFpyArOB5BsNyn2Eg=='
    enc_b64 = 'bYSFRtwz5tNGWxeBETJ9ViV9wlvcJQ7wv1mRrHKEthIW8kYdzPxsdVSJbJahMsv9RwSBE0a3McAZZKkhuF6htsg1fAX5bWLKt2k38y4bTTKzyjjQd9Rs91gJOF/MeTzApDqHZyw19h0PF3fYmgj+zMZy5kRF5FUnvDoC3QIUro4rlyT8D7IKufEQDByUxoVidkQQR35xU6kq/5eGp+dXVw=='
    
    print('=== 独立AES解密测试 ===')
    print(f'Key: {key_b64}')
    print(f'IV: {iv_b64}')
    print(f'Encrypted: {enc_b64[:50]}...')
    print()
    
    try:
        # 1. Base64解码
        key = base64.b64decode(key_b64)
        iv = base64.b64decode(iv_b64)
        cipher_data = base64.b64decode(enc_b64)
        print(f'✓ Base64解码成功 - Key长度: {len(key)}, IV长度: {len(iv)}, 密文长度: {len(cipher_data)}')
        
        # 2. 长度校验
        if len(key) not in (16, 24):
            print(f'✗ Key长度错误: {len(key)} (期望16或24)')
            return False
        if len(iv) != 16:
            print(f'✗ IV长度错误: {len(iv)} (期望16)')
            return False
        if len(cipher_data) % 16 != 0:
            print(f'✗ 密文长度错误: {len(cipher_data)} (需为16的整数倍)')
            return False
        print('✓ 长度校验通过')
        
        # 3. AES解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(cipher_data)
        print(f'✓ AES解密成功，解密后数据长度: {len(decrypted)}')
        print(f'  解密后数据末尾字节: {[b for b in decrypted[-16:]]}')
        
        # 4. 尝试多种去填充方法
        plaintext = None
        
        # 方法1: 标准PKCS7
        try:
            pad_len = decrypted[-1]
            if 1 <= pad_len <= 16:
                padding = decrypted[-pad_len:]
                if all(b == pad_len for b in padding):
                    plaintext = decrypted[:-pad_len]
                    print(f'✓ 标准PKCS7去填充成功，填充长度: {pad_len}')
        except Exception as e:
            print(f'✗ 标准PKCS7去填充失败: {e}')
        
        # 方法2: 查找JSON结束符
        if plaintext is None:
            print('尝试查找JSON结束符...')
            for i in range(len(decrypted) - 1, max(0, len(decrypted) - 50), -1):
                if decrypted[i] in [125, 93, 34]:  # }, ], "
                    plaintext = decrypted[:i+1]
                    print(f'✓ 通过查找JSON结束符去填充，位置: {i}, 长度: {len(plaintext)}')
                    break
        
        # 方法3: 去除零填充
        if plaintext is None:
            plaintext = decrypted.rstrip(b'\x00')
            if len(plaintext) < len(decrypted):
                print(f'✓ 去除零填充，长度从{len(decrypted)}变为{len(plaintext)}')
            else:
                plaintext = decrypted
                print('使用原始解密数据')
        
        print(f'最终明文长度: {len(plaintext)}')
        print(f'明文数据(hex): {plaintext.hex()}')
        print(f'明文数据(bytes): {[b for b in plaintext]}')
        
        # 5. 尝试多种编码解码
        text = None
        for encoding in ['utf-8', 'latin-1', 'ascii']:
            try:
                text = plaintext.decode(encoding)
                print(f'✓ {encoding}解码成功: {repr(text)}')
                break
            except Exception as e:
                print(f'✗ {encoding}解码失败: {e}')
        
        if text is None:
            # 尝试忽略错误
            try:
                text = plaintext.decode('utf-8', errors='ignore')
                print(f'✓ UTF-8忽略错误解码: {repr(text)}')
            except Exception as e:
                print(f'✗ 所有解码方法都失败: {e}')
                return False
        
        # 6. JSON解析
        try:
            payload = json.loads(text)
            print(f'✓ JSON解析成功: {payload}')
            
            # 提取手机号
            phone = payload.get('phoneNumber') or payload.get('purePhoneNumber') or payload.get('phone')
            if phone:
                print(f'✓ 成功提取手机号: {phone}')
                return True
            else:
                print(f'✗ 未找到手机号字段，可用字段: {list(payload.keys())}')
                return False
                
        except Exception as e:
            print(f'✗ JSON解析失败: {e}')
            print(f'  尝试解析的文本: {repr(text)}')
            return False
            
    except Exception as e:
        print(f'✗ 测试过程中发生错误: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_aes_decrypt()
    if success:
        print('\n🎉 解密测试成功！')
    else:
        print('\n❌ 解密测试失败！')
