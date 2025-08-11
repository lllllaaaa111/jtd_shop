#!/usr/bin/env python3
"""
测试数据创建脚本
用于创建JTD Shop项目的基本测试数据
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App_backend.settings')
django.setup()

from user_management.models import User
from product_management.models import Category, Product
from order_management.models import Order, OrderItem, Cart
from content_management.models import Article, Banner, Notice
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

def create_test_data():
    """创建测试数据"""
    print("开始创建测试数据...")
    
    # 创建测试用户
    print("👥 创建测试用户...")
    try:
        # 检查是否已存在admin用户
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
                'role': 'admin'
            }
        )
        if created:
            admin_user.set_password('Gg666666')
            admin_user.save()
            print("✅ 创建admin用户")
        else:
            print("✅ admin用户已存在")
        
        # 创建测试用户
        test_users = [
            {'username': 'test_user1', 'email': 'user1@example.com', 'role': 'user'},
            {'username': 'test_user2', 'email': 'user2@example.com', 'role': 'user'},
            {'username': 'test_user3', 'email': 'user3@example.com', 'role': 'vip'},
        ]
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': False,
                    'is_superuser': False,
                    'role': user_data['role']
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                print(f"✅ 创建用户: {user_data['username']}")
            else:
                print(f"✅ 用户已存在: {user_data['username']}")
                
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
    
    # 创建商品分类
    print("\n🛍️ 创建商品分类...")
    try:
        categories = [
            {'name': '电子产品', 'description': '各类电子产品'},
            {'name': '服装鞋帽', 'description': '时尚服装和鞋帽'},
            {'name': '家居用品', 'description': '家居生活用品'},
            {'name': '食品饮料', 'description': '各类食品和饮料'},
        ]
        
        created_categories = []
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                print(f"✅ 创建分类: {cat_data['name']}")
            else:
                print(f"✅ 分类已存在: {cat_data['name']}")
            created_categories.append(category)
            
    except Exception as e:
        print(f"❌ 创建商品分类失败: {e}")
        created_categories = []
    
    # 创建商品
    print("\n🛍️ 创建测试商品...")
    try:
        if created_categories:
            products_data = [
                {
                    'name': 'iPhone 15 Pro',
                    'description': '最新款iPhone，性能强劲',
                    'price': Decimal('8999.00'),
                    'original_price': Decimal('9999.00'),
                    'stock': 50,
                    'sales': 100,
                    'manufacturer': 'Apple',
                    'category': created_categories[0]
                },
                {
                    'name': 'MacBook Air M2',
                    'description': '轻薄便携的笔记本电脑',
                    'price': Decimal('7999.00'),
                    'original_price': Decimal('8999.00'),
                    'stock': 30,
                    'sales': 80,
                    'manufacturer': 'Apple',
                    'category': created_categories[0]
                },
                {
                    'name': 'Nike运动鞋',
                    'description': '舒适透气的运动鞋',
                    'price': Decimal('599.00'),
                    'original_price': Decimal('699.00'),
                    'stock': 200,
                    'sales': 500,
                    'manufacturer': 'Nike',
                    'category': created_categories[1]
                },
                {
                    'name': '智能手表',
                    'description': '功能丰富的智能手表',
                    'price': Decimal('1299.00'),
                    'original_price': Decimal('1499.00'),
                    'stock': 100,
                    'sales': 200,
                    'manufacturer': '小米',
                    'category': created_categories[0]
                }
            ]
            
            created_products = []
            for prod_data in products_data:
                product, created = Product.objects.get_or_create(
                    name=prod_data['name'],
                    defaults=prod_data
                )
                if created:
                    print(f"✅ 创建商品: {prod_data['name']}")
                else:
                    print(f"✅ 商品已存在: {prod_data['name']}")
                created_products.append(product)
        else:
            print("⚠️ 没有可用的分类，跳过商品创建")
            created_products = []
            
    except Exception as e:
        print(f"❌ 创建商品失败: {e}")
        created_products = []
    
    # 创建订单
    print("\n📦 创建测试订单...")
    try:
        if created_products and created_categories:
            # 获取第一个用户作为订单用户
            test_user = User.objects.filter(username='test_user1').first()
            if test_user:
                # 创建订单
                order = Order.objects.create(
                    user=test_user,
                    total_amount=Decimal('9598.00'),
                    status='paid',
                    payment_method='alipay',
                    shipping_address='北京市朝阳区xxx街道',
                    delivery_address='上海市浦东新区xxx路',
                    recipient_name='张三',
                    recipient_phone='13800138000',
                    notes='请尽快发货',
                    paid_at=timezone.now() - timedelta(days=1)
                )
                print(f"✅ 创建订单: {order.order_number}")
                
                # 创建订单项
                for i, product in enumerate(created_products[:2]):
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=1,
                        price=product.price
                    )
                    print(f"✅ 添加订单项: {product.name}")
            else:
                print("⚠️ 没有找到测试用户，跳过订单创建")
        else:
            print("⚠️ 没有可用的商品，跳过订单创建")
            
    except Exception as e:
        print(f"❌ 创建订单失败: {e}")
    
    # 创建文章
    print("\n📝 创建测试文章...")
    try:
        articles_data = [
            {
                'title': '如何选择适合自己的电子产品',
                'content': '在当今科技快速发展的时代，选择适合自己的电子产品变得越来越重要...',
                'summary': '本文介绍了选择电子产品时需要考虑的几个重要因素',
                'author': admin_user,
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=5)
            },
            {
                'title': '2024年最值得购买的数码产品',
                'content': '随着技术的不断进步，2024年涌现出了许多优秀的数码产品...',
                'summary': '盘点2024年最值得购买的数码产品',
                'author': admin_user,
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=3)
            },
            {
                'title': '购物指南：如何避免买到假货',
                'content': '在网购盛行的今天，如何避免买到假货成为了消费者最关心的问题...',
                'summary': '实用的购物防伪指南',
                'author': admin_user,
                'is_published': True,
                'published_at': timezone.now() - timedelta(days=1)
            }
        ]
        
        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults=article_data
            )
            if created:
                print(f"✅ 创建文章: {article_data['title']}")
            else:
                print(f"✅ 文章已存在: {article_data['title']}")
                
    except Exception as e:
        print(f"❌ 创建文章失败: {e}")
    
    # 创建系统公告
    print("\n📢 创建系统公告...")
    try:
        notices_data = [
            {
                'title': '系统维护通知',
                'content': '系统将于今晚22:00-24:00进行维护，期间可能无法正常访问，请提前做好准备。',
                'is_important': True,
                'is_active': True
            },
            {
                'title': '新功能上线',
                'content': '我们新增了商品评价功能，用户现在可以对购买的商品进行评价和打分。',
                'is_important': False,
                'is_active': True
            }
        ]
        
        for notice_data in notices_data:
            notice, created = Notice.objects.get_or_create(
                title=notice_data['title'],
                defaults=notice_data
            )
            if created:
                print(f"✅ 创建公告: {notice_data['title']}")
            else:
                print(f"✅ 公告已存在: {notice_data['title']}")
                
    except Exception as e:
        print(f"❌ 创建公告失败: {e}")
    
    print("\n✅ 测试数据创建完成！")
    print("\n📊 数据统计:")
    print(f"  用户总数: {User.objects.count()}")
    print(f"  商品分类总数: {Category.objects.count()}")
    print(f"  商品总数: {Product.objects.count()}")
    print(f"  订单总数: {Order.objects.count()}")
    print(f"  文章总数: {Article.objects.count()}")
    print(f"  公告总数: {Notice.objects.count()}")
    
    # 显示所有用户
    print("\n👥 用户列表:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email}) - {user.get_role_display()}")

def check_models():
    """检查可用的模型"""
    print("🔍 检查可用的模型...")
    from django.apps import apps
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django'):
            continue
        print(f"\n📦 应用: {app_config.name}")
        for model in app_config.get_models():
            print(f"  - {model.__name__}")

if __name__ == "__main__":
    print("=" * 50)
    print("JTD Shop 测试数据创建工具")
    print("=" * 50)
    
    # 检查模型
    check_models()
    
    # 创建测试数据
    create_test_data()
    
    print("\n" + "=" * 50)
    print("测试数据创建完成！")
    print("=" * 50) 