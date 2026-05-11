"""
File: admin.py
Mô tả: Cấu hình giao diện quản trị (Django Admin) cho ứng dụng shop xe máy.
Bao gồm các tùy chỉnh hiển thị, bộ lọc, tìm kiếm và tích hợp nhập liệu nhanh (Inlines).
"""

from django.contrib import admin
from .models import Category, Brand, Motorcycle, Review, Variation

# 1. Quản lý các dòng biến thể ngay bên trong trang chỉnh sửa xe
class VariationInline(admin.TabularInline):
    """
    Cho phép quản lý (thêm/sửa/xóa) các biến thể (Variation) trực tiếp
    ngay trên giao diện chỉnh sửa của dòng xe (Motorcycle).
    Hiển thị dưới dạng bảng (Tabular).
    """
    model = Variation
    extra = 1  # Số dòng trống mặc định để thêm nhanh biến thể mới
    fields = ['name', 'color', 'price'] # Các trường dữ liệu sẽ hiển thị trong bảng

@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    """
    Tùy chỉnh giao diện quản trị cho Model Motorcycle.
    Tích hợp VariationInline để quản lý phiên bản và giá cùng một lúc.
    """
    list_display = ['name', 'brand', 'category', 'get_price_range']
    list_filter = ['brand', 'category']
    search_fields = ['name']
    inlines = [VariationInline] # Nhúng bảng biến thể vào trang chi tiết xe

    def get_price_range(self, obj):
        """
        Tính toán và hiển thị khoảng giá từ thấp nhất đến cao nhất của dòng xe.
        
        Args:
            obj (Motorcycle): Đối tượng xe hiện tại đang được hiển thị.
        
        Returns:
            str: Chuỗi ký tự định dạng khoảng giá (VNĐ) hoặc thông báo nếu chưa có giá.
        """
        variations = obj.variations.all()
        if variations:
            prices = [v.price for v in variations]
            return f"{min(prices):,.0f} - {max(prices):,.0f} VNĐ"
        return "Chưa có giá"
    
    get_price_range.short_description = 'Khoảng giá'

# 2. Quản lý chi tiết từng Biến thể (nếu muốn sửa lẻ)
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    """
    Giao diện quản lý riêng biệt cho các biến thể xe.
    Hỗ trợ tìm kiếm theo tên xe mẹ và lọc theo đặc tính màu sắc/phiên bản.
    """
    list_display = ['motorcycle', 'name', 'color', 'price']
    list_filter = ['name', 'color']
    search_fields = ['motorcycle__name', 'name']

# Các Model hỗ trợ
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Quản lý thương hiệu xe. Tự động tạo slug từ tên hãng.
    """
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Quản lý danh mục/loại xe. Tự động tạo slug từ tên danh mục.
    """
    prepopulated_fields = {'slug': ('name',)}

# Đăng ký Model Review theo cách mặc định
admin.site.register(Review)