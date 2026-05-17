from django.urls import path
from . import views

urlpatterns = [
    # Trang chủ và danh sách
    path('', views.trang_chu, name='trang_chu'),
    path('san-pham/', views.danh_sach_xe, name='danh_sach_xe'),
    path('xe/<int:id>/', views.chi_tiet_xe, name='chi_tiet_xe'),
    path('dich-vu/', views.dich_vu_view, name='dich_vu'),
    path('tin-tuc/', views.tin_tuc, name='tin_tuc'),

    # Quy trình thanh toán
    path('gui-danh-gia/<int:xe_id>/', views.gui_danh_gia, name='gui_danh_gia'),
    path('thanh-toan/thong-tin/<int:xe_id>/', views.nhap_thong_tin, name='nhap_thong_tin'),
    path('thanh-toan/quet-ma/<int:order_id>/', views.quet_ma_qr, name='quet_ma_qr'),
    path('thanh-toan/thanh-cong/<int:order_id>/', views.thanh_toan_thanh_cong, name='thanh_toan_thanh_cong'),
    path('thanh-toan/hoa-don/<int:order_id>/', views.xuat_hoa_don_pdf, name='xuat_hoa_don'),

    # Điện thoại quét QR mở URL này để xác nhận
    path('thanh-toan/xac-nhan-qr/<int:order_id>/<str:token>/', views.xac_nhan_qr_mobile, name='xac_nhan_qr_mobile'),

    # Trang checkout polling endpoint này để biết điện thoại đã quét chưa
    path('thanh-toan/kiem-tra-qr/<int:order_id>/', views.kiem_tra_qr_status, name='kiem_tra_qr_status'),
]