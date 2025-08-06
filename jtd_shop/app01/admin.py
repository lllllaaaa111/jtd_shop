from django.contrib import admin

# Register your models here.
# 注意：Welcome和Mine模型已经迁移到其他模块
# Welcome -> content_management
# Mine -> user_management

# app01模块现在只包含核心功能，没有自己的数据模型
# 如果需要注册其他模型，请在这里添加