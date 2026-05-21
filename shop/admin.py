"""
File: admin.py
Mô tả: Cấu hình giao diện quản trị (Django Admin) cho ứng dụng shop xe máy.
Bao gồm các tùy chỉnh hiển thị, bộ lọc, tìm kiếm và tích hợp nhập liệu nhanh (Inlines).
"""

from django.contrib import admin
from .models import Category, Brand, Motorcycle, Review, Variation, Order
from .utils import order_manager_queue
class VariationInline(admin.TabularInline):
    """
    Inline admin cho model Variation, hiển thị trực tiếp bên trong trang chỉnh sửa Motorcycle.

    Cho phép thêm, sửa, xóa các biến thể xe (phiên bản, màu sắc, giá)
    mà không cần rời khỏi trang quản lý xe.

    Attributes:
        model (Model): Model Variation được liên kết.
        extra (int): Số dòng trống mặc định hiển thị để nhập thêm biến thể mới.
        fields (list): Các trường hiển thị trong inline gồm tên, màu sắc và giá.
    """

    model = Variation
    extra = 1
    fields = ['name', 'color', 'price']


@admin.register(Motorcycle)
class MotorcycleAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Motorcycle.

    Hiển thị danh sách xe máy kèm thông tin thương hiệu, danh mục và khoảng giá.
    Tích hợp VariationInline để quản lý biến thể trực tiếp trên trang xe.

    Attributes:
        list_display (list): Các cột hiển thị trong danh sách gồm tên, hãng, danh mục và khoảng giá.
        list_filter (list): Bộ lọc bên phải theo hãng và danh mục.
        search_fields (list): Trường tìm kiếm theo tên xe.
        inlines (list): Danh sách inline tích hợp (VariationInline).
    """

    list_display = ['name', 'brand', 'category', 'get_price_range']
    list_filter = ['brand', 'category']
    search_fields = ['name']
    inlines = [VariationInline]

    def get_price_range(self, obj):
        """
        Tính và trả về khoảng giá của xe dựa trên các biến thể hiện có.

        Duyệt qua tất cả biến thể (Variation) của xe, lấy giá thấp nhất
        và cao nhất để hiển thị dưới dạng chuỗi có định dạng VNĐ.

        Args:
            obj (Motorcycle): Đối tượng xe máy đang được hiển thị.

        Returns:
            str: Chuỗi khoảng giá dạng "X - Y VNĐ" nếu có biến thể,
                 hoặc "Chưa có giá" nếu chưa có biến thể nào.
        """
        variations = obj.variations.all()
        if variations:
            prices = [v.price for v in variations]
            return f"{min(prices):,.0f} - {max(prices):,.0f} VNĐ"
        return "Chưa có giá"

    get_price_range.short_description = 'Khoảng giá'


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Variation.

    Cho phép quản lý độc lập các biến thể xe (phiên bản, màu sắc, giá)
    với khả năng lọc và tìm kiếm theo nhiều tiêu chí.

    Attributes:
        list_display (list): Các cột hiển thị gồm tên xe, phiên bản, màu và giá.
        list_filter (list): Bộ lọc theo tên phiên bản và màu sắc.
        search_fields (list): Tìm kiếm theo tên xe hoặc tên phiên bản.
    """

    list_display = ['motorcycle', 'name', 'color', 'price']
    list_filter = ['name', 'color']
    search_fields = ['motorcycle__name', 'name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Brand (Hãng xe).

    Tự động tạo slug từ tên hãng khi nhập liệu, giúp tạo URL thân thiện
    mà không cần nhập thủ công.

    Attributes:
        prepopulated_fields (dict): Tự động điền trường slug dựa trên trường name.
    """

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Category (Danh mục xe).

    Tự động tạo slug từ tên danh mục khi nhập liệu, hỗ trợ tạo URL SEO-friendly.

    Attributes:
        prepopulated_fields (dict): Tự động điền trường slug dựa trên trường name.
    """

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Review (Đánh giá xe).

    Hiển thị danh sách đánh giá kèm tên người dùng, điểm xếp hạng và thời gian tạo.
    Hỗ trợ lọc theo điểm và tìm kiếm theo tên hoặc nội dung đánh giá.

    Attributes:
        list_display (list): Các cột hiển thị gồm tên, điểm đánh giá và ngày tạo.
        list_filter (list): Bộ lọc theo điểm xếp hạng (rating).
        search_fields (list): Tìm kiếm theo tên người dùng hoặc nội dung đánh giá.
    """

    list_display = ['name', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['name', 'content']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Cấu hình trang quản trị cho model Order (Đơn đặt hàng).

    Hiển thị đầy đủ thông tin khách hàng và đơn hàng trong danh sách,
    hỗ trợ lọc theo trạng thái, tìm kiếm theo thông tin khách hàng.
    Trang chi tiết được cấu hình dạng chỉ đọc (readonly) với các nhóm
    thông tin rõ ràng bằng fieldsets.

    Attributes:
        list_display (list): Các cột hiển thị đầy đủ thông tin khách hàng và đơn hàng.
        list_filter (list): Bộ lọc theo trạng thái đơn hàng và ngày tạo.
        search_fields (list): Tìm kiếm theo tên, SĐT và địa chỉ khách hàng.
        ordering (list): Sắp xếp danh sách theo thời gian tạo mới nhất lên đầu.
        readonly_fields (list): Các trường chỉ đọc, không cho phép chỉnh sửa trực tiếp.
        fieldsets (tuple): Nhóm các trường thành 2 phần: thông tin khách hàng và đơn hàng.
    """

    list_display = [
        'id', 'customer_name', 'customer_phone',
        'customer_address', 'customer_birthday', 'customer_gender',
        'motorcycle', 'get_phien_ban', 'get_mau_xe', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_address']
    ordering = ['-created_at']

    def get_phien_ban(self, obj):
        """
        Lấy tên phiên bản (Variation) rẻ nhất của xe trong đơn hàng.

        Truy vấn biến thể có giá thấp nhất liên quan đến xe trong đơn,
        thường dùng để hiển thị phiên bản cơ bản/tiêu chuẩn của xe.

        Args:
            obj (Order): Đối tượng đơn hàng đang được hiển thị.

        Returns:
            str: Tên phiên bản nếu tồn tại biến thể, hoặc 'N/A' nếu không có.
        """
        variation = obj.motorcycle.variations.order_by('price').first()
        return variation.name if variation else 'N/A'

    get_phien_ban.short_description = 'Phiên bản'

    def get_mau_xe(self, obj):
        """
        Lấy màu sắc của biến thể (Variation) rẻ nhất của xe trong đơn hàng.

        Truy vấn biến thể có giá thấp nhất liên quan đến xe trong đơn,
        lấy thông tin màu sắc tương ứng để hiển thị trong danh sách đơn hàng.

        Args:
            obj (Order): Đối tượng đơn hàng đang được hiển thị.

        Returns:
            str: Màu sắc của biến thể nếu tồn tại, hoặc 'N/A' nếu không có.
        """
        variation = obj.motorcycle.variations.order_by('price').first()
        return variation.color if variation else 'N/A'

    get_mau_xe.short_description = 'Màu sắc'

    readonly_fields = [
        'id', 'motorcycle', 'customer_name', 'customer_phone',
        'customer_address', 'customer_birthday', 'customer_gender',
        'status', 'created_at', 'qr_scanned'
    ]
    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': (
                'customer_name', 'customer_phone',
                'customer_address', 'customer_birthday', 'customer_gender'
            )
        }),
        ('Thông tin đơn hàng', {
            'fields': ('motorcycle', 'status', 'qr_scanned', 'created_at')
        }),
    )
    def changelist_view(self, request, extra_context=None):
        # Mỗi lần admin mở danh sách đơn hàng → cleanup tự động
        order_manager_queue.cleanup_expired_orders()
        return super().changelist_view(request, extra_context)