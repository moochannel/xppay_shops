# Generated by Django 2.0.1 on 2018-02-16 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopapproval',
            name='in_qrcode',
            field=models.CharField(
                blank=True,
                help_text='PDF内に表示するQRコードに埋め込む文字列を指定します',
                max_length=2000,
                verbose_name='QRコード用文字列'
            ),
        ),
    ]