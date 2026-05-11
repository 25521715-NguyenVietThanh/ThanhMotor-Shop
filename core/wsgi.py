"""
File này cung cấp một đối tượng có thể gọi được (callable) ở cấp độ module với tên gọi là application.

Đối tượng này được các máy chủ web chuẩn WSGI sử dụng để giao tiếp với dự án của bạn nhằm phục vụ các yêu cầu từ phía người dùng.

Để biết thêm thông tin về file này, hãy xem tại:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
