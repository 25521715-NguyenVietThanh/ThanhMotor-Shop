# 🏍️ ThanhMotor Shop

Web bán xe máy trực tuyến xây dựng bằng **Django**, hỗ trợ thanh toán qua mã QR và xuất hóa đơn PDF.

---

## 📋 Giới thiệu

ThanhMotor Shop là ứng dụng web quản lý và bán xe máy chính hãng (Honda, Yamaha, VinFast...). Người dùng có thể duyệt sản phẩm, lọc theo hãng/loại xe, đặt mua và thanh toán qua QR code, sau đó nhận hóa đơn PDF chuyên nghiệp.

---

## ✨ Tính năng chính

- Duyệt danh sách xe máy với bộ lọc theo **hãng**, **loại xe**, **giá**
- Tìm kiếm nâng cao bằng thuật toán **Linear Search** ưu tiên kết quả
- Xem chi tiết xe, chọn **phiên bản** và **màu sắc** theo từng biến thể
- Đặt hàng và **thanh toán qua mã QR** (điện thoại quét là xác nhận)
- Xuất **hóa đơn PDF** chuyên nghiệp sau khi thanh toán thành công
- Hiển thị **đánh giá khách hàng**
- Quản lý đơn hàng với **hàng đợi tự động dọn** đơn hết hạn (24h)
- Gợi ý xe cùng hãng ở trang chi tiết

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Django 4.2+ |
| Database | SQLite3 |
| Xử lý ảnh | Pillow |
| Tạo mã QR | qrcode |
| Xuất PDF | ReportLab |
| Frontend | Bootstrap 5.3, Font Awesome 6 |
| Template Engine | Django Templates |

---

## 📁 Cấu trúc thư mục

```
Project_BanXe_Fixed/
│
├── core/                   # Cấu hình Django (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── shop/                   # App chính
│   ├── models.py           # Brand, Category, Motorcycle, Variation, Review, Order
│   ├── views.py            # Controller xử lý các trang
│   ├── urls.py             # Định tuyến URL
│   ├── utils.py            # Linear Search, Timsort, Doubly Linked List, Queue
│   ├── admin.py            # Quản trị Django Admin
│   ├── migrations/         # Lịch sử thay đổi database
│   └── templates/shop/     # Giao diện HTML
│       ├── home.html
│       ├── index.html
│       ├── detail.html
│       ├── checkout_info.html
│       ├── checkout_qr.html
│       ├── checkout_confirm_mobile.html
│       ├── checkout_success.html
│       ├── dich_vu.html
│       └── tin_tuc.html
│
├── media/                  # Ảnh xe upload (không commit lên Git)
│   └── .gitkeep
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Cài đặt và chạy

### 1. Clone repository

```bash
git clone https://github.com/username/Project_BanXe.git
cd Project_BanXe
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Tạo database

```bash
python manage.py migrate
```

### 5. Tạo tài khoản admin

```bash
python manage.py createsuperuser
```

### 6. Chạy server

```bash
python manage.py runserver
```

Truy cập tại: **http://127.0.0.1:8000**  
Trang quản trị: **http://127.0.0.1:8000/admin**

---

## 🗄️ Cấu trúc Database

```
Brand ──────────┐
                ▼
Category ──► Motorcycle ──► Variation (phiên bản + màu + giá)
                │
                └──► Order (đơn hàng khách)

Review (đánh giá độc lập)
```

---

## 🔄 Luồng thanh toán

```
Chọn xe  →  Nhập thông tin  →  Quét mã QR  →  Xác nhận  →  Xuất PDF hóa đơn
```

- Mỗi đơn hàng được đẩy vào **Queue (FIFO)** khi tạo
- Đơn chưa thanh toán sau **24 giờ** sẽ tự động bị xóa
- Luồng các bước thanh toán quản lý bằng **Doubly Linked List**

---

## 📦 Yêu cầu hệ thống

- Python **3.10+**
- pip
- Git

---

## 🚀 Deploy lên PythonAnywhere

1. Upload code lên GitHub
2. Đăng nhập [pythonanywhere.com](https://www.pythonanywhere.com)
3. Mở Bash console, clone repo:
   ```bash
   git clone https://github.com/username/Project_BanXe.git
   ```
4. Cài thư viện và cấu hình Web app theo hướng dẫn của PythonAnywhere
5. Đặt biến môi trường `DJANGO_SECRET_KEY` trong mục **Environment variables**

---

## 👤 Tác giả

**Nguyễn Viết Thành**  
📧 25521715@gm.uit.edu.vn  
🏫 Trường Đại học Công nghệ Thông tin – UIT  

---

## 📄 Giấy phép

Dự án phục vụ mục đích học tập. Không sử dụng cho mục đích thương mại.
