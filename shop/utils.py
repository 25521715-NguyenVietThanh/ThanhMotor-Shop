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

    ket_qua_cuoi_cung = ket_qua_uu_tien + ket_qua_phu

    return ket_qua_cuoi_cung


def sort_xe_theo_gia(danh_sach_xe, order='asc'):
    """
    Sắp xếp danh sách xe theo giá sử dụng thuật toán Timsort (built-in của Python).

    Tiêu chí sắp xếp dựa trên giá thấp nhất (min_price) của các biến thể xe.
    Xe nào chưa có biến thể sẽ được tính là giá 0 để tránh lỗi.

    Args:
        danh_sach_xe (QuerySet/list): Danh sách xe cần sắp xếp.
        order (str): 'asc' để sắp xếp tăng dần, 'desc' để giảm dần.

    Returns:
        list: Danh sách xe đã sắp xếp theo giá.
    """
    xe_list = list(danh_sach_xe)

    def lay_gia_thap_nhat(xe):
        bien_the_re_nhat = xe.variations.order_by('price').first()

        if bien_the_re_nhat is None:
            return 0

        return bien_the_re_nhat.price

    if order == 'desc':
        chieu_giam_dan = True
    else:
        chieu_giam_dan = False

    xe_list.sort(key=lay_gia_thap_nhat, reverse=chieu_giam_dan)

    return xe_list


class StepNode:
    """
    Một nút (node) đơn lẻ trong danh sách liên kết đôi.
    Đại diện cho một bước cụ thể trong quy trình thanh toán.

    Attributes:
        name (str): Tên định danh nội bộ của bước (ví dụ: 'info', 'qr').
        url_name (str): Tên URL Django dùng để điều hướng đến bước này.
        prev (StepNode | None): Con trỏ đến nút trước đó (bước trước).
        next (StepNode | None): Con trỏ đến nút tiếp theo (bước sau).
    """

    def __init__(self, name, url_name):
        self.name = name
        self.url_name = url_name
        self.prev = None
        self.next = None

    def __repr__(self):
        ten_buoc_truoc = self.prev.name if self.prev else 'None'
        ten_buoc_sau = self.next.name if self.next else 'None'
        return f"StepNode(name='{self.name}', prev='{ten_buoc_truoc}', next='{ten_buoc_sau}')"


class CheckoutFlow:
    """
    Quản lý luồng thanh toán bằng cấu trúc Doubly Linked List.

    Mỗi bước thanh toán là một StepNode được liên kết 2 chiều với bước
    trước và bước sau. Điều này cho phép điều hướng "Quay lại" hoặc
    "Tiếp theo" một cách linh hoạt mà không cần hardcode thứ tự.

    Attributes:
        steps (dict): Ánh xạ tên bước → StepNode, dùng để tra cứu nhanh.
        head (StepNode | None): Bước đầu tiên trong luồng.
        tail (StepNode | None): Bước cuối cùng trong luồng.
    """

    def __init__(self):
        self.steps = {}
        self.head = None
        self.tail = None

    def add_step(self, name, url_name):
        """
        Thêm một bước mới vào cuối quy trình thanh toán.

        Nút mới sẽ được nối với nút đuôi hiện tại (nếu có),
        sau đó trở thành nút đuôi mới của danh sách.

        Args:
            name (str): Tên định danh nội bộ của bước.
            url_name (str): Tên URL Django tương ứng.
        """
        nut_moi = StepNode(name, url_name)

        if self.head is None:
            self.head = nut_moi
            self.tail = nut_moi
        else:
            nut_moi.prev = self.tail
            self.tail.next = nut_moi
            self.tail = nut_moi

        self.steps[name] = nut_moi

    def get_back_url(self, current_name):
        """
        Lấy URL của bước liền trước bước hiện tại.

        Dùng khi người dùng nhấn nút "Quay lại" để biết cần
        redirect về trang nào.

        Args:
            current_name (str): Tên định danh của bước đang đứng.

        Returns:
            str | None: url_name của bước trước đó,
                        hoặc None nếu đang ở bước đầu tiên.
        """
        nut_hien_tai = self.steps.get(current_name)

        if nut_hien_tai is None:
            return None

        if nut_hien_tai.prev is None:
            return None

        return nut_hien_tai.prev.url_name

    def get_next_url(self, current_name):
        """
        Lấy URL của bước liền sau bước hiện tại.

        Dùng khi người dùng hoàn thành một bước và cần chuyển tiếp.

        Args:
            current_name (str): Tên định danh của bước đang đứng.

        Returns:
            str | None: url_name của bước tiếp theo,
                        hoặc None nếu đang ở bước cuối cùng.
        """
        nut_hien_tai = self.steps.get(current_name)

        if nut_hien_tai is None:
            return None

        if nut_hien_tai.next is None:
            return None

        return nut_hien_tai.next.url_name

    def __len__(self):
        """Trả về tổng số bước hiện có trong luồng thanh toán."""
        return len(self.steps)

    def __repr__(self):
        """Hiển thị thứ tự các bước theo chiều từ đầu đến đuôi."""
        thu_tu_cac_buoc = []
        nut_hien_tai = self.head

        while nut_hien_tai is not None:
            thu_tu_cac_buoc.append(nut_hien_tai.name)
            nut_hien_tai = nut_hien_tai.next

        return f"CheckoutFlow({' → '.join(thu_tu_cac_buoc)})"


payment_flow = CheckoutFlow()
payment_flow.add_step('info', 'nhap_thong_tin')
payment_flow.add_step('qr', 'quet_ma_qr')
payment_flow.add_step('success', 'thanh_toan_thanh_cong')


class OrderQueue:
    """
    Quản lý hàng đợi đơn hàng tạm thời theo cơ chế FIFO (First In - First Out).

    Đơn hàng vào trước sẽ được xử lý và dọn dẹp trước.
    Hỗ trợ cơ chế tự động xóa các đơn hàng pending đã quá 24 giờ
    mà chưa được thanh toán, giúp giữ database sạch sẽ.

    Attributes:
        items (deque): Hàng đợi nội bộ chứa các đối tượng Order.
    """

    def __init__(self):
        self.items = deque()

    def enqueue(self, order_obj):
        """
        Thêm một đơn hàng mới vào cuối hàng đợi.

        Được gọi ngay sau khi khách hàng đặt hàng thành công
        để theo dõi trạng thái xử lý.

        Args:
            order_obj (Order): Đối tượng đơn hàng vừa được tạo.
        """
        self.items.append(order_obj)

    def dequeue(self):
        """
        Lấy và xóa đơn hàng ở đầu hàng đợi (đơn cũ nhất).

        Returns:
            Order | None: Đơn hàng cũ nhất, hoặc None nếu hàng đợi rỗng.
        """
        if len(self.items) == 0:
            return None

        don_hang_cu_nhat = self.items.popleft()
        return don_hang_cu_nhat

    def cleanup_expired_orders(self):
        """
        Duyệt từ đầu hàng đợi và xóa các đơn hàng pending đã quá hạn 24 giờ.

        Chỉ xóa những đơn có trạng thái 'pending' (chưa thanh toán).
        Đơn đã thanh toán hoặc đã hủy sẽ không bị xóa dù đã quá 24 giờ.
        Dừng lại ngay khi gặp đơn chưa hết hạn (vì hàng đợi theo thứ tự thời gian).

        Side effects:
            - Xóa các bản ghi Order hết hạn khỏi database.
            - Xóa các nút tương ứng khỏi deque nội bộ.
        """
        thoi_gian_hien_tai = timezone.now()
        nguong_het_han = timedelta(hours=24)

        while len(self.items) > 0:
            don_hang_dau_hang = self.items[0]

            thoi_gian_ton_tai = thoi_gian_hien_tai - don_hang_dau_hang.created_at

            if thoi_gian_ton_tai <= nguong_het_han:
                break

            don_hang_het_han = self.items.popleft()

            if don_hang_het_han.status == 'pending':
                don_hang_het_han.delete()

    def is_empty(self):
        """
        Kiểm tra hàng đợi có đang rỗng hay không.

        Returns:
            bool: True nếu không có đơn hàng nào, False nếu có.
        """
        return len(self.items) == 0

    def __len__(self):
        """Trả về số lượng đơn hàng hiện đang trong hàng đợi."""
        return len(self.items)

    def __repr__(self):
        """Hiển thị số lượng đơn hàng đang trong hàng đợi."""
        so_don = len(self.items)
        return f"OrderQueue(so_don_hang_dang_cho={so_don})"


order_manager_queue = OrderQueue()