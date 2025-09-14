from django.contrib import admin
from .models import Category, Product, ProductImage, ProductDescription


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    ordering = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'order')


class ProductDescriptionInline(admin.TabularInline):
    model = ProductDescription
    extra = 1
    fields = ('description_image', 'order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'sales', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'manufacturer')
    ordering = ('-created_at',)
    inlines = [ProductImageInline, ProductDescriptionInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'category', 'manufacturer')
        }),
        ('价格和库存', {
            'fields': ('price', 'original_price', 'stock', 'sales')
        }),
        ('状态', {
            'fields': ('is_active',)
        }),
    )


# 商品图片和描述管理不在主admin中显示，通过商品内联管理 