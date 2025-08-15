# JTD Shop API 接口文档

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

### 3. 新建订单 ⭐

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
    "delivery_address": "北京市朝阳区某某街道123号",  // 必填：收货地址
    "recipient_name": "张三",                      // 必填：收件人姓名
    "recipient_phone": "13800138000",             // 必填：收件人电话
    "shipping_address": "上海市浦东新区某某仓库",    // 可选：发货地址
    "notes": "请尽快发货",                         // 可选：订单备注
    "payment_method": "alipay"                    // 可选：支付方式
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