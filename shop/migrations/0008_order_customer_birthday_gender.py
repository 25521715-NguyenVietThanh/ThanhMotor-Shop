from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='customer_birthday',
            field=models.CharField(blank=True, max_length=20, verbose_name='Ngày sinh'),
        ),
        migrations.AddField(
            model_name='order',
            name='customer_gender',
            field=models.CharField(blank=True, max_length=10, verbose_name='Giới tính'),
        ),
    ]
