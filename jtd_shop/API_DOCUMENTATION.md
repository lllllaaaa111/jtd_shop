# JTD Shop API 接口文档

## 项目概述
JTD Shop 是一个基于 Django 的电商管理系统，提供完整的用户管理、商品管理、订单管理、内容管理和系统管理功能。

## 基础信息
- **基础URL**: `http://localhost:8000`
- **API版本**: v1.0
- **数据格式**: JSON
- **认证方式**: 待定

## 接口分类

### 1. 核心功能模块 (smart/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 首页接口 | GET | `/smart/index/` | 获取首页数据 | ✅ |
| 电影列表 | GET | `/smart/films/` | 获取电影列表数据 | ✅ |
| 随机数据 | GET | `/smart/random/` | 获取随机数据 | ✅ |

### 2. 用户管理模块 (users/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 用户列表 | GET | `/users/list/` | 获取用户列表 | ✅ |
| 用户详情 | GET | `/users/detail/{user_id}/` | 获取指定用户详情 | ✅ |
| 创建用户 | POST | `/users/create/` | 创建新用户 | ✅ |
| 更新用户 | PUT | `/users/update/{user_id}/` | 更新用户信息 | ✅ |
| 删除用户 | DELETE | `/users/delete/{user_id}/` | 删除用户 | ✅ |
| 获取头像 | GET | `/users/avatar/` | 获取用户头像 | ✅ |
| 头像列表 | GET | `/users/avatar/list/` | 获取用户头像列表 | ✅ |
| 上传头像 | POST | `/users/avatar/upload/` | 上传用户头像 | ✅ |
| 删除头像 | DELETE | `/users/avatar/delete/` | 删除用户头像 | ✅ |
| 设置头像 | POST | `/users/avatar/set/` | 设置用户头像 | ✅ |

### 3. 商品管理模块 (products/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 分类列表 | GET | `/products/category/list/` | 获取商品分类列表 | ✅ |
| 商品列表 | GET | `/products/list/` | 获取商品列表 | ✅ |
| 商品详情 | GET | `/products/detail/{product_id}/` | 获取指定商品详情 | ✅ |

### 4. 订单管理模块 (orders/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 订单列表 | GET | `/orders/list/` | 获取订单列表 | ✅ |
| 订单详情 | GET | `/orders/detail/{order_id}/` | 获取指定订单详情 | ✅ |
| 购物车列表 | GET | `/orders/cart/list/` | 获取购物车列表 | ✅ |

### 5. 内容管理模块 (content/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 欢迎页面 | GET | `/content/welcome/` | 获取欢迎页面数据 | ✅ |
| 欢迎图片列表 | GET | `/content/welcome/list/` | 获取欢迎图片列表 | ✅ |
| 轮播图列表 | GET | `/content/banner/list/` | 获取轮播图列表 | ✅ |
| 文章列表 | GET | `/content/article/list/` | 获取文章列表 | ✅ |
| 文章详情 | GET | `/content/article/detail/{article_id}/` | 获取指定文章详情 | ✅ |
| 系统公告列表 | GET | `/content/notice/list/` | 获取系统公告列表 | ✅ |

### 6. 系统管理模块 (system/)

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 系统配置列表 | GET | `/system/config/list/` | 获取系统配置列表 | ✅ |
| 操作日志列表 | GET | `/system/log/list/` | 获取操作日志列表 | ✅ |
| 文件上传记录 | GET | `/system/file/list/` | 获取文件上传记录 | ✅ |
| 数据备份列表 | GET | `/system/backup/list/` | 获取数据备份列表 | ✅ |

### 7. Django管理后台

| 接口名称 | 请求方法 | 路径 | 描述 | 状态 |
|---------|---------|------|------|------|
| 管理后台 | GET | `/admin/` | Django管理后台 | ✅ |

## 请求示例

### 创建用户
```bash
curl -X POST http://localhost:8000/users/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 获取用户列表
```bash
curl -X GET http://localhost:8000/users/list/
```

### 获取商品详情
```bash
curl -X GET http://localhost:8000/products/detail/1/
```

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "error message",
  "data": null
}
```

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 测试工具

项目提供了自动化测试脚本 `test_api.py`，可以一键测试所有接口：

```bash
cd /home/wjj/data/jtd_shop/jtd_shop
python3 test_api.py
```

## 注意事项

1. 所有接口都需要确保服务器正在运行
2. 部分接口可能需要认证，具体认证方式待定
3. 文件上传接口需要特殊的请求格式
4. 建议在生产环境中使用HTTPS

## 更新日志

- v1.0 (2024-08-07): 初始版本，包含所有基础接口 