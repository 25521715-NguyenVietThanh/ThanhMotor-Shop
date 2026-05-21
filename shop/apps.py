from django.apps import AppConfig



from django.apps import AppConfig

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        from django.utils import timezone
        from datetime import timedelta
        from .utils import order_manager_queue

        # Chỉ load khi DB đã sẵn sàng
        try:
            from .models import Order
            nguong = timezone.now() - timedelta(hours=24)
            don_con_han = Order.objects.filter(
                status='pending',
                created_at__gte=nguong
            ).order_by('created_at')
            for order in don_con_han:
                order_manager_queue.enqueue(order)
        except Exception:
            pass