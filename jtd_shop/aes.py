import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_wechat_phone(encrypted_data_b64: str, session_key_b64: str, iv_b64: str) -> dict:
    """
    解密微信小程序手机号加密数据
    :param encrypted_data_b64: 加密数据（Base64）
    :param session_key_b64: 会话密钥（Base64）
    :param iv_b64: 初始化向量（Base64）
    :return: 解密后的字典（含手机号等信息）
    """
    try:
        # Base64解码
        key = base64.b64decode(session_key_b64)
        iv = base64.b64decode(iv_b64)
        encrypted_data = base64.b64decode(encrypted_data_b64)
        
        # 校验密钥和IV长度
        if len(key) != 16:  # 微信固定使用AES-128
            raise ValueError("会话密钥长度必须为16字节")
        if len(iv) != 16:
            raise ValueError("IV长度必须为16字节")
        
        # AES-CBC解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)
        
        # PKCS7去填充
        plaintext = unpad(decrypted, AES.block_size).decode('utf-8')
        
        # 解析JSON
        return json.loads(plaintext)
    
    except Exception as e:
        raise ValueError(f"解密失败: {str(e)}")

# 您的输入数据
encrypted_data = "bYSFRtwz5tNGWxeBETJ9ViV9wlvcJQ7wv1mRrHKEthIW8kYdzPxsdVSJbJahMsv9RwSBE0a3McAZZKkhuF6htsg1fAX5bWLKt2k38y4bTTKzyjjQd9Rs91gJOF/MeTzApDqHZyw19h0PF3fYmgj+zMZy5kRF5FUnvDoC3QIUro4rlyT8D7IKufEQDByUxoVidkQQR35xU6kq/5eGp+dXVw=="
session_key = "0b3nSH0w3VGMz53A372w3HQObh0nSH0G"
iv = "StShheFpyArOB5BsNyn2Eg=="

# 执行解密
try:
    result = decrypt_wechat_phone(encrypted_data, session_key, iv)
    print("解密结果:", result)
except ValueError as e:
    print("错误:", e)