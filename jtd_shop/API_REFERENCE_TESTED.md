# JTD Shop 接口文档（基于测试结果）

- 生成时间: 2025-08-08
- 基础 URL: http://localhost:8000
- 认证说明: 默认使用 DRF 全局权限与认证
  - DEFAULT_AUTHENTICATION_CLASSES: SessionAuthentication, BasicAuthentication
  - DEFAULT_PERMISSION_CLASSES: IsAuthenticated（未覆写的 DRF 视图默认需要认证）
  - CSRF: 使用 SessionAuthentication 的 POST/PUT/DELETE 需携带 CSRF（浏览器/同域）。BasicAuth 一般无需 CSRF，但具体视图可能仍受中间件影响

---

## 1. 认证与用户

### 1.1 登录（Session 登录）
- 方法: POST
- 路径: `/users/login/`
- 认证: 允许匿名访问，成功后建立会话（Session）
- 入参（JSON）:
```json
{"username": "<string>", "password": "<string>"}
```
- 成功响应（200）示例:
```json
{"code": 200, "msg": "登录成功", "result": {"user_id": 6, "username": "root", "email": "root@example.com", "is_staff": true}}
```
- 失败响应（401）:
```json
{"code": 401, "msg": "用户名或密码错误", "result": null}
```
- curl（示例）:
```bash
curl -X POST http://localhost:8000/users/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"root","password":"Gg666666"}'
```

### 1.2 注册
- 方法: POST
- 路径: `/users/register/`
- 认证: 允许匿名，但受 CSRF 保护（Session 方式）。建议携带 CSRF 或改用 BasicAuth 作为认证方式
- 入参（JSON）:
```json
{"username":"demo","email":"demo@example.com","password":"pass123456","password_confirm":"pass123456"}
```
- 成功响应（201）:
```json
{"code":201,"msg":"注册成功","result":{"user_id":8,"username":"demo","email":"demo@example.com"}}
```
- 常见错误（403）:
```json
{"detail":"CSRF Failed: CSRF token missing."}
```
- curl（BasicAuth 方式免 CSRF，若后端允许）:
```bash
curl -u root:Gg666666 -X POST http://localhost:8000/users/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","email":"demo@example.com","password":"pass123456","password_confirm":"pass123456"}'
```
- curl（Session+CSRF 方式）:
```bash
curl -c cookies.txt http://localhost:8000/admin/login/ >/dev/null
CSRF=$(grep csrftoken cookies.txt | awk '{print $7}')
curl -b cookies.txt -X POST http://localhost:8000/users/register/ \
  -H "X-CSRFToken: $CSRF" -H 'Referer: http://localhost:8000/admin/login/' \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","email":"demo@example.com","password":"pass123456","password_confirm":"pass123456"}'
```

### 1.3 当前用户信息
- 方法: GET
- 路径: `/users/info/`
- 认证: 需要登录（Session）
- 响应（200）:
```json
{"code":200,"msg":"success","result":{"id":6,"username":"root","email":"root@example.com", "role":"admin"}}
```

### 1.4 用户列表
- 方法: GET
- 路径: `/users/list/`
- 认证: 需要认证（测试中使用 BasicAuth 通过）
- 响应（200，节选）:
```json
{"code":200,"msg":"success","result":[{"id":6,"username":"root"},{"id":1,"username":"admin"}]}
```

### 1.5 用户详情
- 方法: GET
- 路径: `/users/detail/{user_id}/`
- 认证: 需要认证
- 响应（200，示例）:
```json
{"code":200,"msg":"success","result":{"id":1,"username":"admin","email":"18258031988@163.com"}}
```

### 1.6 头像相关（公开）
- 获取头像: GET `/users/avatar/`（公开，可能返回404表示无头像）
- 头像列表: GET `/users/avatar/list/`（公开）

---

## 2. 商品（需要认证）

### 2.1 分类列表
- 方法: GET
- 路径: `/products/category/list/`
- 认证: 需要认证
- 响应（200，节选）:
```json
{"code":200,"msg":"success","result":[{"id":4,"name":"电子产品"},{"id":5,"name":"服装鞋帽"}]}
```

### 2.2 商品列表
- 方法: GET
- 路径: `/products/list/`
- 认证: 需要认证
- 响应（200，节选）:
```json
{"code":200,"msg":"success","result":[{"id":6,"name":"智能手表","price":"1299.00"}]}
```

### 2.3 商品详情
- 方法: GET
- 路径: `/products/detail/{product_id}/`
- 认证: 需要认证
- 响应（200，示例）:
```json
{"code":200,"msg":"success","result":{"id":1,"name":"原味玉米芝麻片","price":"10.00"}}
```

---

## 3. 订单（需要认证）

### 3.1 订单列表
- 方法: GET
- 路径: `/orders/list/`
- 认证: 需要认证
- 响应（200）:
```json
{"code":200,"msg":"success","result":[]}
```

### 3.2 订单详情
- 方法: GET
- 路径: `/orders/detail/{order_id}/`
- 认证: 需要认证
- 响应（200/404/500）:
```json
{"code":200,"msg":"success","result":{"id":1,"order_number":"ORD2025...","items":[...]}}
```
- 说明: 若 ID 不存在将返回 404 或 500（视实现），建议先创建订单再查询

### 3.3 购物车列表
- 方法: GET
- 路径: `/orders/cart/list/`
- 认证: 需要认证
- 响应（200）:
```json
{"code":200,"msg":"success","result":[]}
```

---

## 4. 内容

### 4.1 欢迎页面（公开）
- 方法: GET
- 路径: `/content/welcome/`
- 响应（200，示例）:
```json
{"code":200,"msg":"success","result":{"title":"欢迎图片","image_url":"http://.../media/welcome/...jpeg"}}
```

### 4.2 欢迎图片列表（公开）
- 方法: GET
- 路径: `/content/welcome/list/`

### 4.3 Banner 列表（默认需要认证）
- 方法: GET
- 路径: `/content/banner/list/`

### 4.4 文章列表/详情（默认需要认证）
- 列表: GET `/content/article/list/`
- 详情: GET `/content/article/detail/{article_id}/`
- 响应（200，示例）:
```json
{"code":200,"msg":"success","result":[{"id":1,"title":"测试文章一","author":"admin"}]}
```

### 4.5 系统公告列表（默认需要认证）
- 方法: GET
- 路径: `/content/notice/list/`

---

## 5. 系统管理（需要认证）

- 系统配置: GET `/system/config/list/`
- 操作日志: GET `/system/log/list/`
- 文件上传记录: GET `/system/file/list/`
- 数据备份列表: GET `/system/backup/list/`

示例（文件上传记录 200）:
```json
{"code":200,"msg":"success","result":[{"id":1,"file_name":"test.txt","file_type":"text/plain"}]}
```

---

## 6. Django 管理后台
- 方法: GET
- 路径: `/admin/`
- 响应: HTML（登录/管理界面，SimpleUI 主题）

---

## 通用调用示例（带 BasicAuth）
```bash
# 用户列表（需要认证）
curl -u root:Gg666666 http://localhost:8000/users/list/

# 商品列表（需要认证）
curl -u root:Gg666666 http://localhost:8000/products/list/

# 欢迎页面（公开）
curl http://localhost:8000/content/welcome/
```

## 注意事项
- CSRF: 所有 Session 认证下的修改类请求需携带 CSRF。非浏览器客户端可优先使用 BasicAuth 或 Token（若提供）
- ID 有效性: 详情类接口请确保 ID 存在（先从列表获取）
- 状态码: 创建类接口遵循 201 Created；查询类接口为 200；错误返回含统一结构 `{code,msg,result}` 