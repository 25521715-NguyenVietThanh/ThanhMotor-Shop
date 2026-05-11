"""
File: models.py
Mô tả: Định nghĩa cấu trúc cơ sở dữ liệu cho hệ thống quản lý cửa hàng xe máy.
Bao gồm thông tin về hãng xe, loại xe, dòng xe, các biến thể chi tiết và đánh giá từ khách hàng.
"""

from django.db import models

class Brand(models.Model):
    """
    Lưu trữ thông tin về các hãng sản xuất xe máy (ví dụ: Honda, Yamaha, Suzuki).
    """
    name = models.CharField(max_length=100, verbose_name="Hãng xe")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Phân loại các dòng xe máy theo đặc điểm sử dụng (ví dụ: Xe tay ga, Xe số, Xe côn tay).
    """
    name = models.CharField(max_length=100, verbose_name="Tên hãng xe")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Motorcycle(models.Model):
    """
    Đại diện cho một dòng xe máy cụ thể trong cửa hàng.
    Chứa các thông tin chung về thương hiệu, chủng loại và mô tả sản phẩm.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Hãng xe", null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Loại xe")
    name = models.CharField(max_length=200, verbose_name="Tên dòng xe")
    image = models.ImageField(upload_to='motorcycles/', blank=True, verbose_name="Hình ảnh đại diện")
    description = models.TextField(blank=True, verbose_name="Mô tả chung")

    def __str__(self): 
        return self.name

    def get_unique_version_count(self):
        """
        Thống kê số lượng các phiên bản khác nhau của dòng xe này.
        Returns:
            int: Tổng số tên phiên bản duy nhất hiện có trong danh sách biến thể.
        """
        return self.variations.values('name').distinct().count()

    def get_unique_color_count(self):
        """
        Thống kê số lượng màu sắc khả dụng của dòng xe này.
        Returns:
            int: Tổng số màu sắc duy nhất hiện có trong danh sách biến thể.
        """
        return self.variations.values('color').distinct().count()

class Variation(models.Model):
    """
    Lưu trữ thông tin chi tiết về từng biến thể của một dòng xe.
    Mỗi biến thể là sự kết hợp cụ thể giữa phiên bản, màu sắc và giá bán tương ứng.
    """
    motorcycle = models.ForeignKey(
        Motorcycle, 
        on_delete=models.CASCADE, 
        related_name='variations', 
        verbose_name="Thuộc dòng xe"
    )
    name = models.CharField(
        max_length=100, 
        verbose_name="Tên phiên bản", 
        help_text="VD: Tiêu chuẩn, Thể thao..."
    )
    color = models.CharField(max_length=100, verbose_name="Màu sắc")
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Giá bán cho màu này")

    def __str__(self):
        return f"{self.motorcycle.name} - {self.name} ({self.color})"

class Review(models.Model):
    """
    Lưu trữ các phản hồi và đánh giá từ khách hàng về chất lượng dịch vụ hoặc sản phẩm.
    """
    name = models.CharField(max_length=100, verbose_name="Tên khách hàng")
    rating = models.IntegerField(default=5, verbose_name="Số sao (1-5)")
    content = models.TextField(verbose_name="Nội dung đánh giá")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} sao"
    
from django.utils import timezone
from datetime import timedelta

class Order(models.Model):
    """
    Quản lý thông tin đơn đặt hàng của khách hàng.
    Lưu trữ chi tiết người mua, sản phẩm lựa chọn và hỗ trợ logic cho 
    hàng đợi xử lý đơn hàng (Order Queue) trong vòng 24 giờ.
    """
    motorcycle = models.ForeignKey('Motorcycle', on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    customer_birthday = models.CharField(max_length=20, blank=True, verbose_name="Ngày sinh")
    customer_gender = models.CharField(max_length=10, blank=True, verbose_name="Giới tính")
    
    # Quản lý trạng thái và thời gian cho Hàng đợi (Queue)
    status = models.CharField(max_length=20, default='pending') # pending, paid, expired
    created_at = models.DateTimeField(auto_now_add=True)
    qr_scanned = models.BooleanField(default=False)
    def is_expired(self):
        """
        Kiểm tra thời hạn hiệu lực của đơn hàng trong hàng đợi.
        
        Returns:
            bool: True nếu đơn hàng đã được tạo quá 24 giờ, ngược lại là False.
        """
        # Kiểm tra xem đơn hàng đã qua 24h chưa
        return timezone.now() > self.created_at + timedelta(hours=24)

    def __str__(self):
        return f"Đơn hàng: {self.customer_name} - {self.motorcycle.name}"