# JTD Shop API 测试报告（root 账号）

- 测试时间: 2025-08-08
- 基础 URL: http://localhost:8000
- 认证账号: root / Gg666666（优先 Session 登录 /users/login/，失败时回退 BasicAuth）
- 原始结果文件: `api_test_results_root.json`

## 总览

| 序号 | 接口名称 | 方法 | 路径 | 状态 | 期望 | 结果 |
|---:|---|---|---|---:|---:|:--|
| 1 | 首页接口 | GET | /smart/index/ | 200 | 200 | 通过 |
| 2 | 电影列表 | GET | /smart/films/ | 200 | 200 | 通过 |
| 3 | 随机数据 | GET | /smart/random/ | 200 | 200 | 通过 |
| 4 | 用户列表 | GET | /users/list/ | 200 | 200 | 通过 |
| 5 | 用户详情 | GET | /users/detail/1/ | 200 | 200 | 通过 |
| 6 | 创建用户 | POST | /users/create/ | 403 | 201 | 失败（缺CSRF） |
| 7 | 获取用户头像 | GET | /users/avatar/ | 200 | 200 | 通过 |
| 8 | 头像列表 | GET | /users/avatar/list/ | 200 | 200 | 通过 |
| 9 | 分类列表 | GET | /products/category/list/ | 200 | 200 | 通过 |
| 10 | 商品列表 | GET | /products/list/ | 200 | 200 | 通过 |
| 11 | 商品详情 | GET | /products/detail/1/ | 200 | 200 | 通过 |
| 12 | 订单列表 | GET | /orders/list/ | 200 | 200 | 通过 |
| 13 | 订单详情 | GET | /orders/detail/1/ | 500 | 200 | 失败（数据不存在） |
| 14 | 购物车列表 | GET | /orders/cart/list/ | 200 | 200 | 通过 |
| 15 | 欢迎页面 | GET | /content/welcome/ | 200 | 200 | 通过 |
| 16 | 欢迎图片列表 | GET | /content/welcome/list/ | 200 | 200 | 通过 |
| 17 | 轮播图列表 | GET | /content/banner/list/ | 200 | 200 | 通过 |
| 18 | 文章列表 | GET | /content/article/list/ | 200 | 200 | 通过 |
| 19 | 文章详情 | GET | /content/article/detail/1/ | 200 | 200 | 通过 |
| 20 | 系统公告列表 | GET | /content/notice/list/ | 200 | 200 | 通过 |
| 21 | 系统配置列表 | GET | /system/config/list/ | 200 | 200 | 通过 |
| 22 | 操作日志列表 | GET | /system/log/list/ | 200 | 200 | 通过 |
| 23 | 文件上传记录 | GET | /system/file/list/ | 200 | 200 | 通过 |
| 24 | 数据备份列表 | GET | /system/backup/list/ | 200 | 200 | 通过 |
| 25 | Django管理后台 | GET | /admin/ | 200 | 200 | 通过 |

备注：
- 创建用户（/users/create/）返回 403，错误为 CSRF token 缺失。该接口受 CSRF 保护，需携带 CSRF 或使用注册接口（/users/register/）。
- 订单详情（/orders/detail/1/）返回 500，提示找不到对应订单。建议先创建订单，或使用有效 ID。

---

## 详细记录（调用方式、入参与出参）

以下内容基于 `api_test_results_root.json`，响应过长的条目做了“已截断”说明。

### 1) 首页接口
- 方法: GET
- 路径: `/smart/index/`
- 入参: 无
- 出参:
```json
{
  "product_name": "油滋滋汉堡",
  "product_price": "16元",
  "description": "汉堡赛高！"
}
```

### 2) 电影列表（响应已截断）
- 方法: GET
- 路径: `/smart/films/`
- 入参: 无
- 出参(节选):
```json
{
  "status": 0,
  "data": {
    "films": [
      {
        "filmId": 7348,
        "name": "向阳·花",
        "director": "冯小刚",
        "category": "剧情|犯罪"
      }
      // ... 共计若干项，已截断
    ],
    "total": 55
  },
  "msg": "ok"
}
```

### 3) 随机数据
- 方法: GET
- 路径: `/smart/random/`
- 入参: 无
- 出参(示例):
```json
[3579724, 25118995, 18946308]
```

### 4) 用户列表
- 方法: GET
- 路径: `/users/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {"id": 2, "username": "test_user1", "email": "user1@example.com"},
    {"id": 3, "username": "test_user2", "email": "user2@example.com"},
    {"id": 1, "username": "admin", "email": "18258031988@163.com"},
    {"id": 6, "username": "root", "email": "602212694@qq.com"}
    // ... 已截断
  ]
}
```

### 5) 用户详情
- 方法: GET
- 路径: `/users/detail/1/`
- 入参: 无
- 出参:
```json
{
  "code": 200,
  "msg": "success",
  "result": {
    "id": 1,
    "username": "admin",
    "email": "18258031988@163.com"
  }
}
```

### 6) 创建用户（失败：缺少CSRF）
- 方法: POST
- 路径: `/users/create/`
- 入参(JSON):
```json
{
  "username": "root_api_user",
  "email": "root_api_user@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123"
}
```
- 出参:
```json
{"detail": "CSRF Failed: CSRF token missing."}
```

### 7) 获取用户头像
- 方法: GET
- 路径: `/users/avatar/`
- 入参: 无
- 出参:
```json
{"code": 404, "msg": "未找到头像图片", "result": null}
```

### 8) 头像列表
- 方法: GET
- 路径: `/users/avatar/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 9) 分类列表
- 方法: GET
- 路径: `/products/category/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {"id": 1, "name": "食品"},
    {"id": 4, "name": "电子产品"}
    // ... 已截断
  ]
}
```

### 10) 商品列表
- 方法: GET
- 路径: `/products/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [
    {"id": 6, "name": "智能手表", "price": "1299.00"},
    {"id": 5, "name": "Nike运动鞋", "price": "599.00"}
    // ... 已截断
  ]
}
```

### 11) 商品详情
- 方法: GET
- 路径: `/products/detail/1/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": {"id": 1, "name": "原味玉米芝麻片", "price": "10.00"}
}
```

### 12) 订单列表
- 方法: GET
- 路径: `/orders/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 13) 订单详情（失败：数据不存在）
- 方法: GET
- 路径: `/orders/detail/1/`
- 入参: 无
- 出参:
```json
{"code": 500, "msg": "服务器错误: No Order matches the given query.", "result": null}
```

### 14) 购物车列表
- 方法: GET
- 路径: `/orders/cart/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 15) 欢迎页面
- 方法: GET
- 路径: `/content/welcome/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": {"id": "1", "title": "欢迎图片", "image_url": "http://localhost:8000/media/..."}
}
```

### 16) 欢迎图片列表
- 方法: GET
- 路径: `/content/welcome/list/`
- 入参: 无
- 出参(节选):
```json
{"code": 200, "msg": "success", "result": [{"id": 1, "title": "欢迎图片"}]}
```

### 17) 轮播图列表
- 方法: GET
- 路径: `/content/banner/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 18) 文章列表
- 方法: GET
- 路径: `/content/article/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [{"id": 1, "title": "测试文章一", "author": "admin"}]
}
```

### 19) 文章详情
- 方法: GET
- 路径: `/content/article/detail/1/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": {"id": 1, "title": "测试文章一", "content": "这是一篇用于测试的文章内容"}
}
```

### 20) 系统公告列表
- 方法: GET
- 路径: `/content/notice/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [{"id": 1, "title": "系统维护通知"}]
}
```

### 21) 系统配置列表
- 方法: GET
- 路径: `/system/config/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 22) 操作日志列表
- 方法: GET
- 路径: `/system/log/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 23) 文件上传记录
- 方法: GET
- 路径: `/system/file/list/`
- 入参: 无
- 出参(节选):
```json
{
  "code": 200,
  "msg": "success",
  "result": [{"id": 1, "file_name": "test.txt", "file_type": "text/plain"}]
}
```

### 24) 数据备份列表
- 方法: GET
- 路径: `/system/backup/list/`
- 入参: 无
- 出参:
```json
{"code": 200, "msg": "success", "result": []}
```

### 25) Django 管理后台（HTML，已截断）
- 方法: GET
- 路径: `/admin/`
- 入参: 无
- 出参: HTML 文本（页面源码，已截断显示）

---

## 建议
- 若要通过接口创建用户，建议：
  - 在同一 Session 内先访问登录页以获取 CSRF，再携带 `X-CSRFToken` 头提交；或
  - 使用开放的注册接口 `/users/register/`（若开放）进行创建。
- 订单详情建议先创建有效订单，再以返回的 ID 进行详情查询。 