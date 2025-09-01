# 微信支付集成配置指南

## 概述

本系统已集成微信支付功能，包括：
1. **签名生成**: 生成微信支付API调用所需的签名头
2. **回调解密**: 解密微信支付回调通知中的加密数据
3. **证书解密**: 解密微信支付平台证书下载接口返回的证书数据

## 配置步骤

### 1. 数据库迁移

首先需要创建数据库表结构：

```bash
cd /data/jtd_backend/jtd_shop
source .venv/bin/activate
python manage.py makemigrations system_management
python manage.py migrate
```

### 2. 配置微信支付参数

#### 方法1: 通过Django Admin配置

1. 访问 `https://jtd.wxdnet.cn:8080/admin/`
2. 使用管理员账号登录
3. 在"系统管理" -> "微信支付配置"中添加配置：
   - **商户号**: 你的微信支付商户号
   - **商户API证书序列号**: 商户API证书的序列号
   - **商户私钥**: PEM格式的RSA私钥文件内容
   - **API V3密钥**: 用于解密回调通知和平台证书的密钥

#### 方法2: 通过settings.py配置

在 `App_backend/settings.py` 中确保以下配置：

```python
# 微信支付配置
WECHAT_APPID = 'your_appid'
WECHAT_SECRET = 'your_secret'
mchid = 'your_mchid'
serial_no = 'your_serial_no'
```

### 3. 安装依赖

确保安装了必要的Python包：

```bash
pip install cryptography
```

## 接口使用

### 1. 生成签名头

**接口**: `POST /system/wechat/certificate/`

**用途**: 生成微信支付API调用所需的签名头

**示例**:
```bash
curl -X POST https://jtd.wxdnet.cn:8080/system/wechat/certificate/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token" \
  -d '{
    "method": "POST",
    "url_path": "/v3/pay/transactions/native",
    "query_string": "",
    "body": "{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\",\"out_trade_no\":\"TEST123456\",\"notify_url\":\"https://example.com/notify\",\"amount\":{\"total\":100,\"currency\":\"CNY\"}}"
  }'
```

### 2. 解密回调通知

**接口**: `POST /system/wechat/callback/decrypt/`

**用途**: 解密微信支付回调通知中的加密数据

**示例**:
```bash
curl -X POST https://jtd.wxdnet.cn:8080/system/wechat/callback/decrypt/ \
  -H "Content-Type: application/json" \
  -d '{
    "resource": {
      "ciphertext": "base64_encoded_ciphertext",
      "nonce": "base64_encoded_nonce",
      "associated_data": ""
    }
  }'
```

### 3. 解密平台证书

**接口**: `POST /system/wechat/certificate/decrypt/`

**用途**: 解密微信支付平台证书下载接口返回的证书数据

**示例**:
```bash
curl -X POST https://jtd.wxdnet.cn:8080/system/wechat/certificate/decrypt/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token" \
  -d '{
    "data": [
      {
        "serial_no": "1234567890ABCDEF",
        "effective_time": "2023-01-01T00:00:00+08:00",
        "expire_time": "2024-01-01T00:00:00+08:00",
        "ciphertext": "base64_encoded_ciphertext",
        "nonce": "base64_encoded_nonce",
        "associated_data": ""
      }
    ]
  }'
```

## 测试

### 运行测试脚本

```bash
cd /data/jtd_backend/jtd_shop
source .venv/bin/activate
python test_wechat_decrypt.py
```

**注意**: 运行测试前请确保：
1. 已配置正确的API V3密钥
2. 后端服务正在运行
3. 网络连接正常

### 手动测试

可以使用Postman或其他API测试工具测试接口功能。

## 安全注意事项

1. **私钥保护**: 商户私钥是敏感信息，请妥善保管
2. **API V3密钥**: 用于解密回调数据，请勿泄露
3. **HTTPS**: 生产环境必须使用HTTPS
4. **权限控制**: 签名生成和证书解密接口需要管理员权限
5. **回调验证**: 建议在回调解密后验证签名

## 常见问题

### Q: 签名生成失败
**A**: 检查以下配置：
- 商户号是否正确
- 商户API证书序列号是否正确
- 商户私钥格式是否为PEM格式

### Q: 回调解密失败
**A**: 检查以下配置：
- API V3密钥是否正确
- 加密参数是否完整（ciphertext、nonce）
- 密钥长度是否为32字节

### Q: 证书解密失败
**A**: 检查以下配置：
- API V3密钥是否正确
- 证书数据格式是否正确
- 加密参数是否完整

## 技术支持

如遇到问题，请检查：
1. Django日志文件
2. 网络连接状态
3. 配置参数正确性
4. 依赖包版本兼容性

## 更新日志

- **v1.0.0**: 初始版本，支持基本的签名生成和回调解密
- **v1.1.0**: 添加平台证书解密功能
- **v1.2.0**: 优化错误处理和日志记录 