# 系统配置管理说明

## 概述

系统配置模块已经重新设计，将微信支付配置整合到统一的系统配置中，避免了功能重复。

## 配置结构

### 系统配置 (SystemConfig)

系统配置使用键值对的方式存储各种配置信息，包括：

- **通用配置**: 系统级别的配置参数
- **微信支付配置**: 微信支付相关的配置参数
- **其他配置**: 其他业务相关的配置参数

### 微信支付配置项

在系统配置中，微信支付相关的配置键包括：

| 配置键 | 说明 | 示例值 |
|--------|------|--------|
| `mchid` | 微信支付商户号 | `1234567890` |
| `serial_no` | 商户API证书序列号 | `12345678901234567890` |
| `private_key` | 商户私钥(PEM格式) | `-----BEGIN PRIVATE KEY-----...` |
| `api_v3_key` | API V3密钥 | `32位随机字符串` |

## 使用方法

### 1. 初始化微信支付配置

运行初始化脚本：

```bash
cd /data/jtd_backend/jtd_shop
source .venv/bin/activate
python manage.py shell < system_management/init_wechat_config.py
```

### 2. 在Django Admin中配置

1. 访问 Django Admin (`/admin/`)
2. 进入"系统管理" → "系统配置"
3. 编辑或创建以下配置项：
   - `mchid`: 填写您的微信支付商户号
   - `serial_no`: 填写商户API证书序列号
   - `private_key`: 粘贴您的商户私钥(PEM格式)
   - `api_v3_key`: 填写API V3密钥

### 3. 在代码中使用

```python
from system_management.models import SystemConfig

# 获取微信支付配置
wechat_configs = SystemConfig.get_wechat_pay_config()
mchid = wechat_configs.get('mchid')
api_v3_key = wechat_configs.get('api_v3_key')

# 获取单个配置值
mchid = SystemConfig.get_config_value('mchid', default='')
```

## 优势

1. **统一管理**: 所有配置都在一个地方管理
2. **避免重复**: 不再需要单独的微信支付配置模型
3. **灵活扩展**: 可以轻松添加新的配置类型
4. **易于维护**: 统一的配置管理界面

## 注意事项

1. 配置键必须唯一
2. 敏感信息（如私钥）建议加密存储
3. 修改配置后需要重启相关服务
4. 建议定期备份配置数据

## 相关文件

- `system_management/models.py`: 数据模型定义
- `system_management/admin.py`: Admin界面配置
- `system_management/init_wechat_config.py`: 初始化脚本
- `system_management/views.py`: API视图（使用新配置系统） 