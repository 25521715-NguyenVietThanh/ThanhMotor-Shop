"""
File: views.py
Mô tả: 
    Module điều hướng chính (Controller) của ứng dụng cửa hàng xe máy.
    Quản lý luồng dữ liệu giữa Models và Templates, tích hợp các thuật toán 
    tìm kiếm, sắp xếp và hệ thống thanh toán/đơn hàng.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.urls import reverse
from datetime import timedelta
import qrcode
import io
import base64

from .models import Motorcycle, Brand, Category, Review, Order
from .utils import linear_search_xe_nang_cao, sort_xe_theo_gia, payment_flow, order_manager_queue

def trang_chu(request):
    """
    Xử lý hiển thị trang chủ của cửa hàng.
    
    Logic:
    - Truy vấn danh sách Category để hiển thị menu.
    - Lấy 6 sản phẩm xe mới nhất (theo ID giảm dần).
    - Lấy 3 đánh giá khách hàng mới nhất.

    Args:
        request (HttpRequest): Đối tượng yêu cầu từ trình duyệt.

    Returns:
        HttpResponse: Render giao diện 'shop/home.html'.
    """
    categories = Category.objects.all()
    xe_moi_nhat = Motorcycle.objects.all().order_by('-id')[:6]
    reviews = Review.objects.all().order_by('-created_at')
    
    return render(request, 'shop/home.html', {
        'categories': categories,
        'xe_moi': xe_moi_nhat,
        'reviews': reviews
    })

def danh_sach_xe(request):
    """
    Xử lý hiển thị danh sách sản phẩm với các bộ lọc và tìm kiếm nâng cao.
    
    Quy trình xử lý:
    1. Lấy toàn bộ danh sách xe từ DB và chuyển thành List để áp dụng thuật toán Python thuần.
    2. Nếu có từ khóa tìm kiếm (q), sử dụng thuật toán Linear Search.
    3. Lọc danh sách dựa trên Brand và Category (nếu có).
    4. Sắp xếp kết quả dựa trên tham số giá (tăng/giảm dần).

    Args:
        request (HttpRequest): Chứa các tham số GET (q, sort, brand, category).

    Returns:
        HttpResponse: Render 'shop/index.html' kèm danh sách xe đã xử lý.
    """
    motorcycles = list(Motorcycle.objects.all())
    brands = Brand.objects.all()
    categories = Category.objects.all()
    
    query = request.GET.get('q', '')
    sort_param = request.GET.get('sort', '')
    brand_slug = request.GET.get('brand')
    cat_slug = request.GET.get('category')

    if query:
        motorcycles = linear_search_xe_nang_cao(motorcycles, query)
    
    if brand_slug:
        motorcycles = [m for m in motorcycles if m.brand.slug == brand_slug]

    if cat_slug:
        motorcycles = [m for m in motorcycles if m.category.slug == cat_slug]

    if sort_param == 'price_asc':
        motorcycles = sort_xe_theo_gia(motorcycles, 'asc')
    elif sort_param == 'price_desc':
        motorcycles = sort_xe_theo_gia(motorcycles, 'desc')

    return render(request, 'shop/index.html', {
        'ds_xe': motorcycles,
        'brands': brands,
        'categories': categories,
        'query': query,
        'sort_order': sort_param
    })

def chi_tiet_xe(request, id):
    """
    Hiển thị thông tin chi tiết của một sản phẩm xe cụ thể.
    
    Chức năng bổ trợ:
    - Gợi ý 4 sản phẩm cùng thương hiệu (liên quan).
    - Hiển thị tối đa 5 đánh giá mới nhất của xe.

    Args:
        request (HttpRequest): Đối tượng yêu cầu.
        id (int): ID (khóa chính) của xe cần truy vấn.

    Returns:
        HttpResponse: Render 'shop/detail.html'.
    """
    xe = get_object_or_404(Motorcycle, id=id)
    categories = Category.objects.all()
    xe_lien_quan = Motorcycle.objects.filter(brand=xe.brand).exclude(id=id)[:4]
    reviews = Review.objects.all().order_by('-created_at')[:5]

    return render(request, 'shop/detail.html', {
        'xe': xe,
        'categories': categories,
        'xe_lien_quan': xe_lien_quan,
        'reviews': reviews
    })

def dich_vu_view(request):
    """Hiển thị trang giới thiệu các dịch vụ hậu mãi và sửa chữa."""
    return render(request, 'shop/dich_vu.html')

def tin_tuc(request):
    """Hiển thị trang tin tức và các chương trình khuyến mãi của cửa hàng."""
    return render(request, 'shop/tin_tuc.html')

def nhap_thong_tin(request, xe_id):
    """
    Xử lý form nhập thông tin khách hàng khi bắt đầu đặt mua xe.
    
    Khi POST:
    - Tạo một bản ghi Order mới với trạng thái 'pending'.
    - Đưa đơn hàng vào hàng đợi xử lý (Queue).
    - Chuyển hướng sang trang quét mã QR.

    Args:
        request (HttpRequest): Chứa dữ liệu form POST (tên, sđt, địa chỉ).
        xe_id (int): ID của chiếc xe khách hàng chọn mua.

    Returns:
        HttpResponse: Render form nhập liệu hoặc Redirect tới trang QR.
    """
    xe = get_object_or_404(Motorcycle, id=xe_id)
    if request.method == 'POST':
        order = Order.objects.create(
            motorcycle=xe,
            customer_name=request.POST.get('name'),
            customer_phone=request.POST.get('phone'),
            customer_address=request.POST.get('address'),
            customer_birthday=request.POST.get('birthday', ''),
            customer_gender=request.POST.get('gender', ''),
            status='pending'
        )
        order_manager_queue.enqueue(order)
        return redirect('quet_ma_qr', order_id=order.id)
    
    return render(request, 'shop/checkout_info.html', {'xe': xe})

def quet_ma_qr(request, order_id):
    """
    Tạo và hiển thị mã QR thanh toán cho đơn hàng.
    
    Cơ chế:
    - Sử dụng thư viện `qrcode` để tạo mã chứa liên kết xác nhận.
    - Chuyển đổi hình ảnh QR sang dạng Base64 để hiển thị trực tiếp trên HTML.

    Args:
        request (HttpRequest): Đối tượng yêu cầu.
        order_id (int): ID đơn hàng cần thanh toán.

    Returns:
        HttpResponse: Render 'shop/checkout_qr.html' kèm mã QR.
    """
    import hashlib
    order = Order.objects.get(id=order_id)

    # Tạo token để xác thực đúng đơn hàng khi điện thoại quét
    qr_token = hashlib.sha256(f"BANXE-SECRET-{order_id}".encode()).hexdigest()[:16]

    # QR encode URL trỏ thẳng về server — điện thoại quét là mở URL này
    qr_url = request.build_absolute_uri(
        reverse('xac_nhan_qr_mobile', args=[order_id, qr_token])
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    variation = order.motorcycle.variations.order_by('price').first()
    gia_xe = variation.price if variation else 0

    return render(request, 'shop/checkout_qr.html', {
        'order': order,
        'qr_code': qr_code_base64,
        'gia_xe': gia_xe,
    })

def xac_nhan_qr_mobile(request, order_id, token):
    """
    Xác thực mã QR được quét từ thiết bị di động thông qua Token bảo mật.
    Cập nhật trạng thái qr_scanned cho đơn hàng.
    """
    import hashlib
    expected_token = hashlib.sha256(f"BANXE-SECRET-{order_id}".encode()).hexdigest()[:16]
    if token != expected_token:
        return HttpResponse("Mã QR không hợp lệ.", status=400)

    order = get_object_or_404(Order, id=order_id)
    order.qr_scanned = True
    order.save()

    return render(request, 'shop/checkout_confirm_mobile.html', {'order_id': order_id})


def kiem_tra_qr_status(request, order_id):
    """API trả về trạng thái quét mã QR dưới dạng JsonResponse (AJAX)."""
    from django.http import JsonResponse
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({'scanned': order.qr_scanned})


def thanh_toan_thanh_cong(request, order_id):
    """
    Xác nhận trạng thái đã thanh toán cho đơn hàng.
    Hỗ trợ cả AJAX (XMLHttpRequest) từ trang QR và truy cập trực tiếp.

    Args:
        request (HttpRequest): Đối tượng yêu cầu.
        order_id (int): ID đơn hàng được xác nhận.

    Returns:
        HttpResponse: JSON nếu là AJAX, hoặc render trang thông báo thành công.
    """
    from django.http import JsonResponse
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'paid':
        order.status = 'paid'
        order.save()
    
    # Nếu gọi từ fetch() (AJAX), trả về JSON để JS tự hiện giao diện
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})

    return render(request, 'shop/checkout_success.html', {'order': order})

def xuat_hoa_don_pdf(request, order_id):
    """
    Xuất hóa đơn dưới dạng file PDF chuyên nghiệp cho đơn hàng đã thanh toán.

    Nội dung hóa đơn bao gồm:
    - Header với tên cửa hàng, logo chữ và thông tin liên hệ.
    - Thông tin chi tiết khách hàng (tên, SĐT, địa chỉ, ngày sinh, giới tính).
    - Thông tin sản phẩm và giá bán.
    - Thời gian giao hàng dự kiến.
    - Hình ảnh xe máy làm nền mờ (watermark) phía sau nội dung.
    - Chân trang với số hóa đơn.

    Args:
        request (HttpRequest): Đối tượng yêu cầu.
        order_id (int): ID đơn hàng cần xuất hóa đơn.

    Returns:
        HttpResponse: File PDF đính kèm.
    """
    import io
    from datetime import timedelta
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    order = get_object_or_404(Order, id=order_id)

    # Lấy biến thể xe (ưu tiên biến thể rẻ nhất)
    variation = order.motorcycle.variations.order_by('price').first()
    gia_xe        = variation.price if variation else 0
    ten_phien_ban = variation.name  if variation else 'Không cung cấp'
    mau_xe        = variation.color if variation else 'Không cung cấp'

    ngay_giao = (order.created_at + timedelta(days=1)).strftime('%d/%m/%Y')
    # Format ngày sinh sang dd/mm/yyyy
    if order.customer_birthday:
        try:
            from datetime import datetime as dt
            ngay_sinh = dt.strptime(str(order.customer_birthday), '%Y-%m-%d').strftime('%d/%m/%Y')
        except Exception:
            ngay_sinh = str(order.customer_birthday)
    else:
        ngay_sinh = 'Khong cung cap'
    gioi_tinh = order.customer_gender   if order.customer_gender   else 'Không cung cấp'

    moto_img_data = None  # watermark image disabled

    # -------- Canvas với watermark --------
    buffer = io.BytesIO()
    page_w, page_h = A4

    class WatermarkCanvas(canvas.Canvas):
        """Canvas tùy chỉnh: vẽ watermark ảnh xe thực + nền trên mỗi trang."""

        def __init__(self, *args, moto_img_data=None, font_bold=None, font_normal=None, **kwargs):
            self._moto_img_data = moto_img_data
            self._font_bold   = font_bold   or 'Helvetica-Bold'
            self._font_normal = font_normal or 'Helvetica'
            super().__init__(*args, **kwargs)

        def showPage(self):
            self._draw_background()
            super().showPage()

        def save(self):
            super().save()

        def _draw_background(self):
            self.saveState()
            # Dải màu xanh đậm trên cùng
            self.setFillColor(colors.HexColor('#0d3b66'))
            self.rect(0, page_h - 3.5*cm, page_w, 3.5*cm, fill=1, stroke=0)
            # Tên cửa hàng căn giữa trong dải xanh
            self.setFillColor(colors.white)
            self.setFont(self._font_bold, 22)
            self.drawCentredString(page_w / 2, page_h - 1.8*cm, 'ThanhMotor Shop')
            self.setFillColor(colors.HexColor('#aad4ff'))
            self.setFont(self._font_normal, 8)
            self.drawCentredString(page_w / 2, page_h - 2.6*cm, 'Khu phố 34, P. Linh Xuân, TP. HCM   |   090 xxx xxxx   |   25521715@gm.uit.edu.vn')
            # Dải accent ở đáy
            self.setFillColor(colors.HexColor('#0d6efd'))
            self.rect(0, 0, page_w, 1.2*cm, fill=1, stroke=0)

            self.restoreState()

    # -------- Đăng ký font DejaVu hỗ trợ tiếng Việt --------
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        pdfmetrics.registerFont(TTFont('DejaVu', 'C:/Windows/Fonts/arial.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Oblique', 'C:/Windows/Fonts/ariali.ttf'))
        FONT_NORMAL = 'DejaVu'
        FONT_BOLD   = 'DejaVu-Bold'
    except Exception:
        FONT_NORMAL = 'Helvetica'
        FONT_BOLD   = 'Helvetica-Bold'

    # -------- Styles --------
    styles = getSampleStyleSheet()

    style_header_name = ParagraphStyle('header_name',
        fontSize=22, leading=26, textColor=colors.white,
        fontName=FONT_BOLD, alignment=TA_LEFT)

    style_header_sub = ParagraphStyle('header_sub',
        fontSize=9, leading=13, textColor=colors.HexColor('#aad4ff'),
        fontName=FONT_NORMAL, alignment=TA_LEFT)

    style_invoice_no = ParagraphStyle('invoice_no',
        fontSize=14, leading=18, textColor=colors.white,
        fontName=FONT_BOLD, alignment=TA_RIGHT)

    style_section_title = ParagraphStyle('section_title',
        fontSize=11, leading=14, textColor=colors.HexColor('#0d3b66'),
        fontName=FONT_BOLD, spaceAfter=4)

    style_body = ParagraphStyle('body',
        fontSize=10, leading=15, textColor=colors.HexColor('#222222'),
        fontName=FONT_NORMAL)

    style_label = ParagraphStyle('label',
        fontSize=9, leading=13, textColor=colors.HexColor('#666666'),
        fontName=FONT_NORMAL)

    style_price = ParagraphStyle('price',
        fontSize=16, leading=20, textColor=colors.HexColor('#c0392b'),
        fontName=FONT_BOLD, alignment=TA_RIGHT)

    style_footer_txt = ParagraphStyle('footer_txt',
        fontSize=8, textColor=colors.white,
        fontName=FONT_NORMAL, alignment=TA_CENTER)

    style_thanks = ParagraphStyle('thanks',
        fontSize=11, leading=16, textColor=colors.HexColor('#0d6efd'),
        fontName=FONT_BOLD, alignment=TA_CENTER)

    # -------- Build content --------
    def build_pdf(canvas_obj, doc):
        pass  # background đã được WatermarkCanvas tự xử lý

    story = []
    col_w = page_w - 4*cm  # nội dung chiều rộng

    # --- HEADER: Tên cửa hàng căn giữa như tiêu đề + số hóa đơn ---
    style_shop_title = ParagraphStyle('shop_title',
        fontSize=26, leading=30, textColor=colors.white,
        fontName=FONT_BOLD, alignment=TA_CENTER)
    style_shop_sub_center = ParagraphStyle('shop_sub_center',
        fontSize=9, leading=13, textColor=colors.HexColor('#aad4ff'),
        fontName=FONT_NORMAL, alignment=TA_CENTER)

    ngay_xuat = order.created_at.strftime('%d/%m/%Y')

    style_invoice_center = ParagraphStyle('invoice_center',
        fontSize=14, leading=18, textColor=colors.HexColor('#0d3b66'),
        fontName=FONT_BOLD, alignment=TA_CENTER)
    style_invoice_date = ParagraphStyle('invoice_date',
        fontSize=9, leading=13, textColor=colors.HexColor('#555555'),
        fontName=FONT_NORMAL, alignment=TA_CENTER)

    story.append(Spacer(1, 3.8*cm))  # chừa chỗ cho dải header màu
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f'HOÁ ĐƠN #{order.id:04d}', style_invoice_center))
    story.append(Paragraph(f'Ngày xuất: {ngay_xuat}', style_invoice_date))
    story.append(Spacer(1, 0.5*cm))

    # --- THÔNG TIN KHÁCH HÀNG ---
    story.append(Paragraph('THÔNG TIN KHÁCH HÀNG', style_section_title))
    story.append(HRFlowable(width=col_w, thickness=1, color=colors.HexColor('#0d6efd'), spaceAfter=8))

    kh_data = [
        [Paragraph('Họ và tên:', style_label),        Paragraph(order.customer_name, style_body),
         Paragraph('Giới tính:', style_label),         Paragraph(gioi_tinh, style_body)],
        [Paragraph('Số điện thoại:', style_label),     Paragraph(order.customer_phone, style_body),
         Paragraph('Ngày sinh:', style_label),          Paragraph(ngay_sinh, style_body)],
        [Paragraph('Địa chỉ nhận xe:', style_label),  Paragraph(order.customer_address, style_body),
         Paragraph('', style_label),                    Paragraph('', style_body)],
    ]
    kh_table = Table(kh_data, colWidths=[col_w*0.18, col_w*0.33, col_w*0.15, col_w*0.34])
    kh_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f6ff')),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#f0f6ff'), colors.white]),
    ]))
    story.append(kh_table)
    story.append(Spacer(1, 0.8*cm))

    # --- THÔNG TIN SẢN PHẨM ---
    story.append(Paragraph('THÔNG TIN SẢN PHẨM', style_section_title))
    story.append(HRFlowable(width=col_w, thickness=1, color=colors.HexColor('#0d6efd'), spaceAfter=8))

    xe_name = order.motorcycle.name
    xe_brand = order.motorcycle.brand.name if order.motorcycle.brand else 'N/A'
    xe_cat   = order.motorcycle.category.name if order.motorcycle.category else 'N/A'
    gia_format = f"{int(gia_xe):,}".replace(',', '.') + ' VNĐ'

    sp_data = [
        [Paragraph('Dòng xe:', style_label),    Paragraph(xe_name, style_body),
         Paragraph('Hãng xe:', style_label),    Paragraph(xe_brand, style_body)],
        [Paragraph('Loại xe:', style_label),    Paragraph(xe_cat, style_body),
         Paragraph('Phiên bản:', style_label),  Paragraph(ten_phien_ban, style_body)],
        [Paragraph('Màu sắc:', style_label),    Paragraph(mau_xe, style_body),
         Paragraph('Trạng thái thanh toán:', style_label), Paragraph('Đã thanh toán', style_body)],
    ]
    sp_table = Table(sp_data, colWidths=[col_w*0.18, col_w*0.33, col_w*0.15, col_w*0.34])
    sp_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#f0f6ff'), colors.white]),
    ]))
    story.append(sp_table)
    story.append(Spacer(1, 0.5*cm))

    # Giá (nổi bật)
    gia_table = Table([[
        Paragraph('THÀNH TIỀN:', ParagraphStyle('price_label',
            fontSize=12, textColor=colors.HexColor('#333'),
            fontName=FONT_BOLD, alignment=TA_LEFT)),
        Paragraph(gia_format, style_price)
    ]], colWidths=[col_w*0.5, col_w*0.5])
    gia_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff3f3')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e74c3c')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(gia_table)
    story.append(Spacer(1, 0.8*cm))

    # --- GIAO HÀNG ---
    story.append(Paragraph('THỜI GIAN GIAO HÀNG', style_section_title))
    story.append(HRFlowable(width=col_w, thickness=1, color=colors.HexColor('#0d6efd'), spaceAfter=8))
    story.append(Paragraph(
        f'Dự kiến giao xe vào ngày <b>{ngay_giao}</b>, từ 07:00 đến 17:00.',
        style_body))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        'Đội ngũ giao hàng sẽ liên hệ trước ít nhất 1 giờ để xác nhận.',
        style_label))
    story.append(Spacer(1, 1.2*cm))

    # --- LỜI CẢM ƠN ---
    story.append(HRFlowable(width=col_w, thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=12))
    story.append(Paragraph('Cảm ơn quý khách đã tin tưởng lựa chọn ThanhMotor Shop!', style_thanks))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        'Mọi thắc mắc xin liên hệ Hotline: 090 xxx xxxx | 25521715@gm.uit.edu.vn',
        ParagraphStyle('contact', fontSize=9, textColor=colors.HexColor('#555'),
                       fontName=FONT_NORMAL, alignment=TA_CENTER)))

    # -------- Render PDF --------
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=0.5*cm, bottomMargin=2*cm,
        title=f'HoaDon_{order.id}',
        author='ThanhMotor Shop'
    )

    def make_canvas(*args, **kwargs):
        return WatermarkCanvas(*args, moto_img_data=moto_img_data,
                               font_bold=FONT_BOLD, font_normal=FONT_NORMAL, **kwargs)

    doc.build(story, canvasmaker=make_canvas)

    pdf_bytes = buffer.getvalue()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="HoaDon_{order.id}.pdf"'
    return response