# Generated by Django 2.0.2 on 2018-03-18 01:58

from django.db import migrations


def copy_url(apps, schema_editor):
    ShopApproval = apps.get_model('shops', 'ShopApproval')
    for approval in ShopApproval.objects.all():
        try:
            approval.in_qrcode = approval.xppay_channel_url
            approval.save(update_fields=['in_qrcode'])
        except BaseException:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0008_shopapproval_xppay_channel_url'),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, reverse_code=copy_url),
        migrations.RemoveField(
            model_name='shopapproval',
            name='in_qrcode',
        ),
    ]