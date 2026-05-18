"""
File: shop/utils.py
Mô tả: Chứa các cấu trúc dữ liệu và thuật toán bổ trợ cho hệ thống cửa hàng xe máy.
Bao gồm:
    - Thuật toán tìm kiếm và sắp xếp sản phẩm.
    - Cấu trúc Doubly Linked List quản lý luồng thanh toán (Checkout Flow).
    - Cấu trúc Queue quản lý và dọn dẹp đơn hàng chờ xử lý.
"""

from collections import deque
from django.utils import timezone
from datetime import timedelta

def linear_search_xe_nang_cao(danh_sach_xe, query):
    """
    Thực hiện thuật toán Tìm kiếm tuyến tính (Linear Search) cải tiến.
    
    Phân loại kết quả thành nhóm khớp đầu từ khóa (ưu tiên cao) và khớp giữa (ưu tiên thấp)
    để tối ưu hóa kết quả tìm kiếm cho người dùng.

    Args:
        danh_sach_xe (list): Danh sách các đối tượng Motorcycle.
        query (str): Từ khóa tìm kiếm.

    Returns:
        list: Danh sách xe đã được sắp xếp theo độ liên quan.
    """
    if not query:
        return danh_sach_xe
    
    query = query.lower().strip()
    ket_qua_uu_tien = []
    ket_qua_phu = []
    
    for xe in danh_sach_xe:
        ten_xe = xe.name.lower()
        if ten_xe.startswith(query):
            ket_qua_uu_tien.append(xe)
        elif query in ten_xe:
            ket_qua_phu.append(xe)
            
    return ket_qua_uu_tien + ket_qua_phu

def sort_xe_theo_gia(danh_sach_xe, order='asc'):
    """
    Sắp xếp danh sách xe sử dụng thuật toán Timsort.
    
    Tiêu chí sắp xếp dựa trên giá thấp nhất (min_price) của các biến thể xe.

    Args:
        danh_sach_xe (QuerySet/list): Danh sách xe cần sắp xếp.
        order (str): 'asc' (tăng dần) hoặc 'desc' (giảm dần).

    Returns:
        list: Danh sách xe đã sắp xếp.
    """
    xe_list = list(danh_sach_xe)
    
    def get_min_price(xe):
        variant = xe.variations.order_by('price').first()
        return variant.price if variant else 0

    xe_list.sort(key=get_min_price, reverse=(order == 'desc'))
    return xe_list



class StepNode:
    """
    Nút trong danh sách liên kết đôi, đại diện cho một bước trong quy trình thanh toán.
    """
    def __init__(self, name, url_name):
        self.name = name          
        self.url_name = url_name 
        self.prev = None         
        self.next = None          

class CheckoutFlow:
    """
    Quản lý luồng thanh toán bằng cấu trúc Doubly Linked List.
    Giúp việc điều hướng "Quay lại" hoặc "Tiếp theo" linh hoạt hơn.
    """
    def __init__(self):
        self.steps = {} 
        self.head = None
        self.tail = None

    def add_step(self, name, url_name):
        """Thêm một bước mới vào cuối quy trình."""
        new_node = StepNode(name, url_name)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.steps[name] = new_node

    def get_back_url(self, current_name):
        """Lấy URL của bước trước đó dựa trên bước hiện tại."""
        node = self.steps.get(current_name)
        return node.prev.url_name if node and node.prev else None


payment_flow = CheckoutFlow()
payment_flow.add_step('info', 'nhap_thong_tin')
payment_flow.add_step('qr', 'quet_ma_qr')
payment_flow.add_step('success', 'thanh_toan_thanh_cong')



class OrderQueue:
    """
    Quản lý hàng đợi đơn hàng tạm thời sử dụng cấu trúc Queue (FIFO).
    Hỗ trợ cơ chế dọn dẹp tự động các đơn hàng hết hạn xử lý.
    """
    def __init__(self):
       
        self.items = deque()

    def enqueue(self, order_obj):
        """Thêm đơn hàng mới vào cuối hàng đợi."""
        self.items.append(order_obj)

    def cleanup_expired_orders(self):
        """
        Duyệt từ đầu hàng đợi và xóa các đơn hàng chưa thanh toán đã quá 24 giờ.
        Giúp giải phóng bộ nhớ và làm sạch dữ liệu rác trong database.
        """
        now = timezone.now()
        while self.items and (now - self.items[0].created_at > timedelta(hours=24)):
            expired_order = self.items.popleft() 
            if expired_order.status == 'pending':
                expired_order.delete() 


order_manager_queue = OrderQueue()