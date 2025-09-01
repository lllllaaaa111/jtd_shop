# JTD Shop API 接口文档

## 目录
- [用户管理](#用户管理)
- [商品管理](#商品管理)
- [订单管理](#订单管理)
- [内容管理](#内容管理)
- [系统管理](#系统管理)

## 📋 文档信息

- **项目名称**: JTD Shop 电商系统
- **API版本**: v1.0
- **基础URL**: `http://localhost:8000`
- **认证方式**: Session认证 / HTTP Basic认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 🔐 认证说明

### 认证方式
1. **Session认证** (推荐)
   - 先调用登录接口获取Session
   - 后续请求自动携带Session信息

2. **HTTP Basic认证**
   - 用户名: `root`
   - 密码: `Gg666666`

### CSRF保护
- 所有POST请求需要CSRF令牌
- 请求头: `X-CSRFToken` 或 `X-Csrftoken`
- 获取方式: 访问 `/admin/` 页面或登录页面

## 📦 订单管理模块

### 1. 获取订单列表

**接口地址**: `GET /orders/list/`

**功能描述**: 获取当前用户的订单列表

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": [
        {
            "id": 1,
            "order_number": "ORD202312011200001",
            "total_amount": "299.00",
            "status": "pending",
            "status_display": "待支付",
            "payment_method": "alipay",
            "created_at": "2023-12-01 12:00:00",
            "paid_at": null
        }
    ]
}
```

**测试结果**: ✅ 成功 (200)

---

### 2. 获取订单详情

**接口地址**: `GET /orders/detail/{order_id}/`

**功能描述**: 获取指定订单的详细信息

**路径参数**:
- `order_id`: 订单ID (整数)

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": {
        "id": 1,
        "order_number": "ORD202312011200001",
        "total_amount": "299.00",
        "status": "pending",
        "status_display": "待支付",
        "payment_method": "alipay",
        "shipping_address": "上海市浦东新区某某仓库",
        "delivery_address": "北京市朝阳区某某街道123号",
        "recipient_name": "张三",
        "recipient_phone": "13800138000",
        "notes": "请尽快发货",
        "items": [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "商品名称",
                "quantity": 2,
                "price": "149.50",
                "total_price": "299.00"
            }
        ],
        "created_at": "2023-12-01 12:00:00",
        "paid_at": null,
        "shipped_at": null,
        "delivered_at": null
    }
}
```

**错误响应**:
```json
{
    "code": 500,
    "msg": "服务器错误: No Order matches the given query.",
    "result": null
}
```

**测试结果**: ❌ 失败 (500) - 订单不存在

---

### 3. 新建订单（从购物车）

**接口地址**: `POST /orders/create/`

**功能描述**: 从购物车创建新订单

**请求头**:
```
Content-Type: application/json
X-CSRFToken: {csrf_token}
```

**请求参数**:
```json
{
    "delivery_address": "北京市朝阳区某某街道123号",
    "recipient_name": "张三",
    "recipient_phone": "13800138000",
    "shipping_address": "上海市浦东新区某某仓库",
    "notes": "请尽快发货",
    "payment_method": "alipay"
}
```

**成功响应**:
```json
{
    "code": 200,
    "msg": "订单创建成功",
    "result": {
        "id": 1,
        "order_number": "ORD202312011200001",
        "total_amount": "299.00",
        "status": "pending",
        "status_display": "待支付",
        "delivery_address": "北京市朝阳区某某街道123号",
        "recipient_name": "张三",
        "recipient_phone": "13800138000",
        "created_at": "2023-12-01 12:00:00",
        "items_count": 2
    }
}
```

**错误响应**:
```json
{
    "code": 400,
    "msg": "购物车为空，无法创建订单",
    "result": null
}
```

**测试结果**: 
- ✅ 业务逻辑验证正常 (400)
- ✅ CSRF保护正常工作
- ⚠️ 需要先添加商品到购物车

---

### 3+. 直接新建订单（不依赖购物车）

**接口地址**: `POST /orders/create-direct/`

**功能描述**: 根据提交的商品项直接创建订单，不依赖购物车。

**请求头**:
```
Content-Type: application/json
X-CSRFToken: {csrf_token}
```

**请求参数**:
```json
{
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ],
  "delivery_address": "北京市朝阳区某某街道123号",
  "recipient_name": "张三",
  "recipient_phone": "13800138000",
  "shipping_address": "上海市浦东新区某某仓库",
  "notes": "请尽快发货",
  "payment_method": "wechat"
}
```

- `items` 为必填数组，元素包含：
  - `product_id` 商品ID
  - `quantity` 数量，必须大于0
- 其余与 `/orders/create/` 相同

**成功响应**:
```json
{
  "code": 200,
  "msg": "订单创建成功",
  "result": {
    "id": 12,
    "order_number": "ORD202501011200001",
    "internal_order_number": "000000001234",
    "total_amount": "399.00",
    "status": "pending",
    "status_display": "待支付",
    "delivery_address": "北京市朝阳区某某街道123号",
    "recipient_name": "张三",
    "recipient_phone": "13800138000",
    "created_at": "2025-01-01 12:00:00"
  }
}
```

**错误响应**:
```json
{
  "code": 400,
  "msg": "items 不能为空且必须为数组",
  "result": null
}
```

---

### 4. 获取购物车列表

**接口地址**: `GET /orders/cart/list/`

**功能描述**: 获取当前用户的购物车商品列表

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": [
        {
            "id": 1,
            "product_id": 1,
            "product_name": "商品名称",
            "quantity": 2,
            "price": "149.50",
            "total_price": "299.00",
            "added_at": "2023-12-01 10:00:00"
        }
    ]
}
```

**测试结果**: ✅ 成功 (200) - 购物车为空

---

## 🛍️ 商品管理模块

### 1. 获取商品分类列表

**接口地址**: `GET /products/category/list/`

**功能描述**: 获取所有商品分类信息

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": [
        {
            "id": 1,
            "name": "电子产品",
            "description": "各类电子产品",
            "parent_id": null,
            "parent_name": null
        }
    ]
}
```

**测试结果**: ✅ 成功 (200)

---

### 2. 获取商品列表

**接口地址**: `GET /products/list/`

**功能描述**: 获取所有商品的列表信息

**请求参数**:
- `limit` (可选): 限制返回的商品数量，必须是大于0的整数

**请求示例**:
```bash
# 获取所有商品
GET /products/list/

# 获取前5个商品
GET /products/list/?limit=5

# 获取前10个商品
GET /products/list/?limit=10
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": {
        "products": [
            {
                "id": 1,
                "name": "iPhone 15",
                "description": "最新款iPhone",
                "price": "5999.00",
                "original_price": "6999.00",
                "stock": 100,
                "sales": 50,
                "manufacturer": "Apple",
                "category_id": 1,
                "category_name": "电子产品",
                "main_image": "http://localhost:8000/media/products/iphone15.jpg",
                "created_at": "2024-01-15 10:30:00"
            }
        ],
        "total_count": 1,
        "limit": 5
    }
}
```

**错误响应**:
```json
{
    "code": 400,
    "msg": "数量参数必须大于0",
    "result": null
}
```

**测试结果**: ✅ 成功 (200)

---

### 3. 获取商品详情

**接口地址**: `GET /products/detail/{product_id}/`

**功能描述**: 获取指定商品的详细信息

**路径参数**:
- `product_id`: 商品ID (整数)

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": {
        "id": 1,
        "name": "iPhone 15",
        "description": "最新款iPhone",
        "price": "5999.00",
        "original_price": "6999.00",
        "stock": 100,
        "sales": 50,
        "manufacturer": "Apple",
        "category_id": 1,
        "category_name": "电子产品",
        "images": [
            {
                "id": 1,
                "image_url": "http://localhost:8000/media/products/iphone15_1.jpg",
                "is_primary": true,
                "order": 1
            }
        ],
        "description_images": [
            {
                "id": 1,
                "image_url": "http://localhost:8000/media/descriptions/iphone15_desc.jpg",
                "order": 1
            }
        ],
        "created_at": "2024-01-15 10:30:00",
        "updated_at": "2024-01-15 10:30:00"
    }
}
```

**测试结果**: ✅ 成功 (200)

---

### 4. 新增商品

**接口地址**: `POST /products/create/`

**功能描述**: 创建新商品，支持上传一张或多张图片

**认证要求**: 需要用户登录（Session认证）

**请求格式**: `multipart/form-data`

**必填字段**:
- `name`: 商品名称（字符串）
- `price`: 价格（大于0的数值）
- `category_id` 或 `category_name`: 商品分类（二选一）

**可选字段**:
- `description`: 商品描述（字符串）
- `original_price`: 原价（大于0的数值）
- `stock`: 库存数量（非负整数）
- `sales`: 销量（非负整数）
- `manufacturer`: 生产厂商（字符串）
- `images`: 商品图片（多文件，字段名：images）

**请求示例**:
```bash
# 基础商品创建（无图片）
curl -b cookies.txt -X POST http://localhost:8000/products/create/ \
  -H "X-CSRFToken: {csrf_token}" \
  -F "name=测试商品" \
  -F "price=99.99" \
  -F "category_name=电子产品" \
  -F "description=这是一个测试商品" \
  -F "stock=10" \
  -F "manufacturer=TestCo"

# 带图片的商品创建
curl -b cookies.txt -X POST http://localhost:8000/products/create/ \
  -H "X-CSRFToken: {csrf_token}" \
  -F "name=图片商品" \
  -F "price=199.99" \
  -F "category_name=电子产品" \
  -F "description=包含图片的商品" \
  -F "original_price=299.99" \
  -F "stock=5" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.png"
```

**响应示例**:
```json
{
    "code": 201,
    "msg": "created",
    "result": {
        "id": 12,
        "name": "图片商品",
        "description": "包含图片的商品",
        "price": "199.99",
        "original_price": "299.99",
        "stock": 5,
        "sales": 0,
        "manufacturer": "",
        "category_id": 1,
        "category_name": "电子产品",
        "images": [
            {
                "id": 21,
                "image_url": "http://localhost:8000/media/products/image1.jpg",
                "is_primary": true,
                "order": 0
            },
            {
                "id": 22,
                "image_url": "http://localhost:8000/media/products/image2.png",
                "is_primary": false,
                "order": 1
            }
        ],
        "created_at": "2024-01-15 12:00:00"
    }
}
```

**错误响应**:
```json
{
    "code": 400,
    "msg": "商品名称为必填项",
    "result": null
}
```

**注意事项**:
- 图片字段名为 `images`，支持多文件上传
- 第一张图片自动设为主图（is_primary=true）
- 图片按上传顺序排序（order字段）
- 分类可通过ID或名称指定，但必须存在且激活
- 价格必须大于0，库存和销量不能为负数

**测试结果**: ✅ 成功 (201)

---

### 5. 按分类名称模糊匹配获取商品

**接口地址**: `GET /products/by-category/`

**功能描述**: 根据分类名称模糊匹配获取商品列表

**请求参数**:
- `category_name` (必需): 分类名称，支持模糊匹配
- `limit` (可选): 限制返回的商品数量，必须是大于0的整数

**请求示例**:
```bash
# 获取所有匹配的商品
GET /products/by-category/?category_name=电子

# 获取前3个匹配的商品
GET /products/by-category/?category_name=电子&limit=3

# 获取前5个匹配的商品
GET /products/by-category/?category_name=服装&limit=5
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": {
        "category_name": "电子",
        "matched_categories": [
            {
                "id": 1,
                "name": "电子产品",
                "description": "各类电子产品"
            }
        ],
        "products": [
            {
                "id": 1,
                "name": "iPhone 15",
                "description": "最新款iPhone",
                "price": "5999.00",
                "original_price": "6999.00",
                "stock": 100,
                "sales": 50,
                "manufacturer": "Apple",
                "category_id": 1,
                "category_name": "电子产品",
                "main_image": "http://localhost:8000/media/products/iphone15.jpg",
                "created_at": "2024-01-15 10:30:00"
            }
        ],
        "total_count": 1,
        "limit": 3
    }
}
```

**错误响应**:
```json
{
    "code": 400,
    "msg": "数量参数必须大于0",
    "result": null
}
```

**测试结果**: ✅ 成功 (200)

---

### 6. 按分类名称精确匹配获取商品

**接口地址**: `GET /products/by-category/{category_name}/`

**功能描述**: 根据分类名称精确匹配获取商品列表

**路径参数**:
- `category_name`: 分类名称，必须完全匹配

**查询参数**:
- `limit` (可选): 限制返回的商品数量，必须是大于0的整数

**请求示例**:
```bash
# 获取所有匹配的商品
GET /products/by-category/电子产品/

# 获取前2个匹配的商品
GET /products/by-category/电子产品/?limit=2

# 获取前10个匹配的商品
GET /products/by-category/服装鞋帽/?limit=10
```

**响应示例**:
```json
{
    "code": 200,
    "msg": "success",
    "result": {
        "category": {
            "id": 1,
            "name": "电子产品",
            "description": "各类电子产品"
        },
        "products": [
            {
                "id": 1,
                "name": "iPhone 15",
                "description": "最新款iPhone",
                "price": "5999.00",
                "original_price": "6999.00",
                "stock": 100,
                "sales": 50,
                "manufacturer": "Apple",
                "category_id": 1,
                "category_name": "电子产品",
                "main_image": "http://localhost:8000/media/products/iphone15.jpg",
                "created_at": "2024-01-15 10:30:00"
            }
        ],
        "total_count": 1,
        "limit": 2
    }
}
```

**错误响应**:
```json
{
    "code": 400,
    "msg": "数量参数必须大于0",
    "result": null
}
```

**测试结果**: ✅ 成功 (200)

---

## 🏷️ 数据模型说明

### 订单状态 (Order Status)
| 状态值 | 状态名称 | 说明 |
|--------|----------|------|
| pending | 待支付 | 订单已创建，等待用户支付 |
| paid | 已支付 | 订单已支付，等待发货 |
| shipped | 已发货 | 订单已发货，运输中 |
| delivered | 已送达 | 订单已送达，等待确认 |
| completed | 已完成 | 订单已完成 |
| cancelled | 已取消 | 订单已取消 |
| refunded | 已退款 | 订单已退款 |

### 支付方式 (Payment Method)
| 支付方式 | 说明 |
|----------|------|
| alipay | 支付宝 |
| wechat | 微信支付 |
| bank | 银行转账 |

## 🧪 测试结果总结

### 接口可用性
| 接口 | 状态 | 说明 |
|------|------|------|
| GET /orders/list/ | ✅ 正常 | 返回空列表 |
| GET /orders/cart/list/ | ✅ 正常 | 返回空购物车 |
| POST /orders/create/ | ✅ 正常 | CSRF保护正常，业务逻辑验证正常 |
| GET /orders/detail/1/ | ❌ 异常 | 订单不存在 |

### 功能验证
- ✅ **认证机制**: Session认证和Basic认证都正常工作
- ✅ **CSRF保护**: 所有POST请求都需要有效的CSRF令牌
- ✅ **数据验证**: 必填字段验证正常工作
- ✅ **业务逻辑**: 购物车为空时正确返回错误信息
- ✅ **错误处理**: 异常情况有适当的错误响应

## 🚀 使用流程

### 1. 获取CSRF令牌
```bash
# 访问admin页面获取CSRF令牌
curl -c cookies.txt http://localhost:8000/admin/
```

### 2. 用户登录
```bash
# 使用Session登录
curl -b cookies.txt -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: {csrf_token}" \
  -d '{"username": "root", "password": "Gg666666"}'
```

### 3. 查看购物车
```bash
curl -b cookies.txt http://localhost:8000/orders/cart/list/
```

### 4. 创建订单
```bash
curl -b cookies.txt -X POST http://localhost:8000/orders/create/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: {csrf_token}" \
  -d '{
    "delivery_address": "北京市朝阳区某某街道123号",
    "recipient_name": "张三",
    "recipient_phone": "13800138000",
    "notes": "请尽快发货"
  }'
```

## ⚠️ 注意事项

1. **CSRF令牌**: 所有POST请求必须包含有效的CSRF令牌
2. **购物车**: 创建订单前必须先在购物车中添加商品
3. **认证**: 所有接口都需要用户认证
4. **数据格式**: 请求和响应都使用JSON格式
5. **错误处理**: 接口会返回详细的错误信息

## 🔧 开发建议

1. **前端集成**: 建议使用Session认证，减少CSRF令牌管理复杂度
2. **错误处理**: 根据返回的code字段判断请求是否成功
3. **数据验证**: 在客户端也进行必填字段验证
4. **用户体验**: 在购物车为空时提供友好的提示信息

## 📞 技术支持

如有问题，请检查：
1. Django服务器是否正常运行
2. 用户认证是否成功
3. CSRF令牌是否有效
4. 购物车中是否有商品 

## 系统管理

### 获取系统配置列表
- **接口**: `GET /system/config/list/`
- **描述**: 获取系统配置列表
- **权限**: 需要管理员权限
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {
      "id": 1,
      "key": "site_name",
      "value": "JTD Shop",
      "description": "网站名称",
      "updated_at": "2024-01-01 12:00:00"
    }
  ]
}
```

### 获取操作日志列表
- **接口**: `GET /system/log/list/`
- **描述**: 获取系统操作日志列表
- **权限**: 需要管理员权限
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {
      "id": 1,
      "user": "admin",
      "action": "CREATE",
      "resource": "Product",
      "resource_id": "123",
      "description": "创建商品",
      "ip_address": "127.0.0.1",
      "created_at": "2024-01-01 12:00:00"
    }
  ]
}
```

### 获取文件上传记录列表
- **接口**: `GET /system/file/list/`
- **描述**: 获取文件上传记录列表
- **权限**: 需要管理员权限
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {
      "id": 1,
      "file_name": "product.jpg",
      "file_path": "/media/products/product.jpg",
      "file_size": 1024000,
      "file_size_mb": 1.0,
      "file_type": "image/jpeg",
      "upload_time": "2024-01-01 12:00:00",
      "user": "admin"
    }
  ]
}
```

### 获取数据备份记录列表
- **接口**: `GET /system/backup/list/`
- **描述**: 获取数据备份记录列表
- **权限**: 需要管理员权限
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {
      "id": 1,
      "backup_name": "daily_backup_20240101",
      "backup_type": "daily",
      "file_path": "/backups/daily_backup_20240101.sql",
      "file_size": 1048576,
      "description": "每日备份",
      "created_by": "system",
      "created_at": "2024-01-01 12:00:00",
      "is_success": true
    }
  ]
}
```

### 生成签名串
- **接口**: `POST /system/signature/generate/`
- **描述**: 生成符合微信支付规范的签名串，包含HTTP请求方法、URL、时间戳、随机串和请求报文主体
- **权限**: 无需认证（允许任何人访问）
- **请求参数**:
```json
{
  "method": "POST",
  "url_path": "/v3/pay/transactions/jsapi",
  "timestamp": 1756735194,
  "nonce_str": "test_nonce_string_12345",
  "body": "{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\"}"
}
```
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": {
    "signature_string": "POST\n/v3/pay/transactions/jsapi\n1756735194\ntest_nonce_string_12345\n{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\"}\n",
    "signature_string_hex": "504f53540a2f76332f7061792f7472616e73616374696f6e732f6a736170690a...",
    "signature_string_ascii": [80, 79, 83, 84, 10, 47, 118, 51, ...],
    "method": "POST",
    "url_path": "/v3/pay/transactions/jsapi",
    "timestamp": 1756735194,
    "nonce_str": "test_nonce_string_12345",
    "body": "{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\"}",
    "note": "签名串格式：HTTP请求方法\\n + URL\\n + 请求时间戳\\n + 请求随机串\\n + 请求报文主体\\n"
  }
}
```

### 获取微信支付证书/签名头
- **接口**: `POST /system/wechat/certificate/`
- **描述**: 生成微信支付API调用所需的签名头
- **权限**: 需要管理员权限
- **请求参数**:
```json
{
  "method": "POST",
  "url_path": "/v3/pay/transactions/native",
  "query_string": "",
  "body": "{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\",\"out_trade_no\":\"TEST123456\",\"notify_url\":\"https://example.com/notify\",\"amount\":{\"total\":100,\"currency\":\"CNY\"}}"
}
```
- **响应示例**:
```json
{
  "code": 200,
  "msg": "success",
  "result": {
    "authorization": "mchid=\"1725611901\",nonce_str=\"c5ac7061fccab6bf3e254dcf98995b8c\",timestamp=\"1704067200\",serial_no=\"4557B9E49272B1D50A48D672BA2BA9581399DBC2\",signature=\"base64_encoded_signature\"",
    "timestamp": 1704067200,
    "nonce_str": "c5ac7061fccab6bf3e254dcf98995b8c",
    "serial_no": "4557B9E49272B1D50A48D672BA2BA9581399DBC2",
    "mchid": "1725611901",
    "signature": "base64_encoded_signature",
    "message": "POST\n/v3/pay/transactions/native\n1704067200\nc5ac7061fccab6bf3e254dcf98995b8c\n{\"appid\":\"wx123456\",\"mchid\":\"1234567890\",\"description\":\"测试商品\",\"out_trade_no\":\"TEST123456\",\"notify_url\":\"https://example.com/notify\",\"amount\":{\"total\":100,\"currency\":\"CNY\"}}\n",
    "canonical_url": "/v3/pay/transactions/native",
    "signature_method": "RSA-SHA256"
  }
}
```

### 解密微信支付回调通知
- **接口**: `POST /system/wechat/callback/decrypt/`
- **描述**: 解密微信支付回调通知中的加密数据
- **权限**: 无需认证（微信回调专用）
- **请求参数**:
```json
{
  "resource": {
    "ciphertext": "base64_encoded_ciphertext",
    "nonce": "base64_encoded_nonce",
    "associated_data": ""
  }
}
```
- **响应示例**:
```json
{
  "code": 200,
  "msg": "解密成功",
  "result": {
    "decrypted_data": {
      "resource_type": "encrypt-resource",
      "event_type": "TRANSACTION.SUCCESS",
      "summary": "支付成功",
      "resource": {
        "transaction_id": "4200001234567890",
        "amount": 100,
        "currency": "CNY"
      }
    },
    "resource_type": "encrypt-resource",
    "event_type": "TRANSACTION.SUCCESS",
    "summary": "支付成功"
  }
}
```

### 解密微信支付平台证书
- **接口**: `POST /system/wechat/certificate/decrypt/`
- **描述**: 解密微信支付平台证书下载接口返回的证书数据
- **权限**: 需要管理员权限
- **请求参数**:
```json
{
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
}
```
- **响应示例**:
```json
{
  "code": 200,
  "msg": "证书解密成功",
  "result": {
    "total_count": 1,
    "success_count": 1,
    "certificates": [
      {
        "serial_no": "1234567890ABCDEF",
        "effective_time": "2023-01-01T00:00:00+08:00",
        "expire_time": "2024-01-01T00:00:00+08:00",
        "decrypted_cert": {
          "serial_no": "1234567890ABCDEF",
          "effective_time": "2023-01-01T00:00:00+08:00",
          "expire_time": "2024-01-01T00:00:00+08:00",
          "encrypt_certificate": "-----BEGIN CERTIFICATE-----..."
        }
      }
    ]
  }
}
```

## 注意事项

### 微信支付配置
1. **商户号 (mchid)**: 微信支付商户号
2. **商户API证书序列号 (serial_no)**: 商户API证书的序列号
3. **商户私钥**: PEM格式的RSA私钥，用于生成签名
4. **API V3密钥**: 用于解密回调通知和平台证书的密钥

### 签名算法
- 使用 `WECHATPAY2-SHA256-RSA2048` 签名算法
- 签名消息格式: `method\nurl\ntimestamp\nnonce_str\nbody\n`
- 支持RSA-SHA256和HMAC-SHA256两种签名方式

### 加密算法
- 使用AES-256-GCM加密算法
- 需要提供ciphertext、nonce和associated_data参数
- 支持Base64编码的加密数据

### 权限控制
- 证书生成和证书解密接口需要管理员权限
- 回调解密接口无需认证，供微信服务器调用
- 所有接口都支持CSRF保护（除回调解密外） 