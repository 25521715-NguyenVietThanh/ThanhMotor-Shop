from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. Đường dẫn cho trang quản trị (Chỉ cần 1 dòng này)
    path('admin/', admin.site.urls),

    # 2. Kết nối toàn bộ các đường dẫn từ app shop vào trang chủ
    path('', include('shop.urls')), 
]

# Serve file media (ảnh sản phẩm) kể cả khi DEBUG = False
# Lưu ý: trên PythonAnywhere cần cấu hình thêm trong dashboard Web > Static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)