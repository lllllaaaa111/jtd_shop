# Gunicorn配置文件
import multiprocessing

# 绑定地址和端口
bind = "127.0.0.1:6580"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 每个工作进程的最大并发连接数
worker_connections = 1000

# 超时设置
timeout = 120
keepalive = 5

# 日志配置（输出到 stdout/stderr，便于 systemd/journal 收集）
accesslog = "-"
errorlog = "-"
loglevel = "info"
umask = 0o022

# 进程名称
proc_name = "jtd_shop"

# # 用户和组
user = "www-data"
group = "www-data"

# 预加载应用
preload_app = True

# 最大请求数
max_requests = 1000
max_requests_jitter = 100

# 重启工作进程
graceful_timeout = 30

# 其他设置
daemon = False
pidfile = "/tmp/gunicorn.pid"
