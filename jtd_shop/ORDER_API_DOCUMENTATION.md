# 订单管理模块 API 文档

## 概述
订单管理模块提供订单的创建、查询、管理等功能的API接口。

## 基础信息
- 基础路径: `/orders/`
- 认证方式: 需要用户认证 (JWT Token)
- 请求格式: JSON
- 响应格式: JSON

## 接口列表

### 1. 获取订单列表
**接口地址:** `GET /orders/list/`

**请求参数:** 无

**响应示例:**
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

### 2. 获取订单详情
**接口地址:** `GET /orders/detail/{order_id}/`

**路径参数:**
- `order_id`: 订单ID (整数)

**响应示例:**
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

### 3. 新建订单 ⭐ 新增接口
**接口地址:** `POST /orders/create/`

**请求参数:**
```json
{
    "delivery_address": "北京市朝阳区某某街道123号",  // 必填：收货地址
    "recipient_name": "张三",                      // 必填：收件人姓名
    "recipient_phone": "13800138000",             // 必填：收件人电话
    "shipping_address": "上海市浦东新区某某仓库",    // 可选：发货地址
    "notes": "请尽快发货",                         // 可选：订单备注
    "payment_method": "alipay"                    // 可选：支付方式 (alipay/wechat/bank)
}
```

**功能说明:**
- 从用户购物车中的商品创建新订单
- 自动计算订单总金额
- 创建订单商品项
- 清空购物车
- 记录订单状态变更日志
- 自动生成唯一订单号

**响应示例:**
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

**错误响应:**
```json
{
    "code": 400,
    "msg": "购物车为空，无法创建订单",
    "result": null
}
```

```json
{
    "code": 400,
    "msg": "缺少必填字段: delivery_address",
    "result": null
}
```

### 4. 获取购物车列表
**接口地址:** `GET /orders/cart/list/`

**请求参数:** 无

**响应示例:**
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

## 订单状态说明

| 状态值 | 状态名称 | 说明 |
|--------|----------|------|
| pending | 待支付 | 订单已创建，等待用户支付 |
| paid | 已支付 | 订单已支付，等待发货 |
| shipped | 已发货 | 订单已发货，运输中 |
| delivered | 已送达 | 订单已送达，等待确认 |
| completed | 已完成 | 订单已完成 |
| cancelled | 已取消 | 订单已取消 |
| refunded | 已退款 | 订单已退款 |

## 支付方式说明

| 支付方式 | 说明 |
|----------|------|
| alipay | 支付宝 |
| wechat | 微信支付 |
| bank | 银行转账 |

## 使用流程

1. **添加商品到购物车** - 通过商品管理模块添加商品到购物车
2. **查看购物车** - 调用 `GET /orders/cart/list/` 查看购物车内容
3. **创建订单** - 调用 `POST /orders/create/` 从购物车创建订单
4. **查看订单** - 调用 `GET /orders/list/` 查看订单列表
5. **查看订单详情** - 调用 `GET /orders/detail/{order_id}/` 查看具体订单

## 注意事项

1. 所有接口都需要用户认证，请在请求头中包含有效的JWT Token
2. 创建订单前请确保购物车中有商品
3. 订单号由系统自动生成，格式为：`ORD + 时间戳 + 用户ID`
4. 订单创建成功后，购物车中的商品会被自动清空
5. 订单状态变更会自动记录到日志中
6. 必填字段：`delivery_address`、`recipient_name`、`recipient_phone`

## 测试

可以使用提供的测试脚本 `test_create_order.py` 来测试新建订单接口：

```bash
python test_create_order.py
```

注意：测试前需要确保Django服务器正在运行，并且有有效的用户认证信息。 