"""
Cấu hình ASGI cho dự án core.

File này cung cấp một đối tượng có thể gọi được (callable) ở cấp độ module với tên gọi là application.

Đối tượng này được các máy chủ web chuẩn ASGI sử dụng để kết nối và chạy dự án của bạn.

Để biết thêm thông tin về file này, hãy xem tại:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()
