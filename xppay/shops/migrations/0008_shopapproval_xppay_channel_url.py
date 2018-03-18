# Generated by Django 2.0.2 on 2018-03-18 01:39

from django.db import migrations, models


def copy_url(apps, schema_editor):
    ShopApproval = apps.get_model('shops', 'ShopApproval')
    for approval in ShopApproval.objects.all():
        try:
            approval.xppay_channel_url = approval.in_qrcode
            approval.save(update_fields=['xppay_channel_url'])
        except BaseException:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0007_auto_20180223_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopapproval',
            name='xppay_channel_url',
            field=models.URLField(
                blank=True,
                help_text='無期限のチャンネル招待リンクを入力します',
                max_length=2000,
                verbose_name='XPpayの店舗チャンネルURL'
            ),
        ),
        migrations.RunPython(copy_url, reverse_code=migrations.RunPython.noop),
    ]
