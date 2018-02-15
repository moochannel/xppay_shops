# Generated by Django 2.0.1 on 2018-02-15 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('list_order', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Benefit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=200, verbose_name='特典内容')),
                ('starts_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='開始日時')),
                ('ends_at', models.DateTimeField(blank=True, null=True, verbose_name='終了日時')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('list_order', models.IntegerField(help_text='数値の低い方が優先されます', verbose_name='表示優先順')),
                ('label', models.CharField(max_length=100, verbose_name='表示名')),
                ('href', models.CharField(blank=True, max_length=300, null=True, verbose_name='リンク')),
            ],
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Employment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invited_at', models.DateTimeField(null=True, verbose_name='招待日時')),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_invides', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.ImageField(help_text='PCでは画像ファイルをファイルボタンにドラッグすると簡単に指定できます', upload_to='shops/origin/%y/%m/%d', verbose_name='店舗画像')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='店舗名')),
                ('business_description', models.CharField(max_length=1000, verbose_name='紹介文')),
                ('zipcode', models.CharField(help_text='ハイフンを入れず7桁の数字で入力してください', max_length=7, verbose_name='郵便番号')),
                ('address1', models.CharField(max_length=100, verbose_name='住所1')),
                ('address2', models.CharField(blank=True, max_length=100, verbose_name='住所2')),
                ('map_url', models.URLField(blank=True, max_length=2000, verbose_name='店舗地図URL')),
                ('slug', models.SlugField(allow_unicode=True, help_text='URLで店舗を識別するための単語を指定します', unique=True, verbose_name='スラッグ')),
                ('discord_for_payment', models.CharField(help_text='XPpayでの支払先に使用するDiscordアカウント名を指定します', max_length=100, verbose_name='支払先Discordアカウント')),
                ('in_qrcode', models.CharField(blank=True, help_text='PDF内に表示するQRコードに埋め込む文字列を指定します', max_length=2000, verbose_name='QRコード用文字列')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shops', to='shops.Area', verbose_name='地域')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shop_creator', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('staffs', models.ManyToManyField(through='shops.Employment', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='shop_updater', to=settings.AUTH_USER_MODEL, verbose_name='更新者')),
            ],
        ),
        migrations.CreateModel(
            name='ShopApproval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_at', models.DateTimeField(auto_now_add=True, verbose_name='申請日時')),
                ('canceled_at', models.DateTimeField(null=True, verbose_name='取り下げ・取消日時')),
                ('approved', models.CharField(choices=[('RE', '申請済み'), ('EX', '審査中'), ('AP', '承認'), ('DE', '否認')], default='RE', max_length=2, verbose_name='承認結果')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('canceled_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='canceled_approvals', to=settings.AUTH_USER_MODEL, verbose_name='取消者')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='request_approvals', to=settings.AUTH_USER_MODEL, verbose_name='申請者')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='shops.Shop')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='update_approvals', to=settings.AUTH_USER_MODEL, verbose_name='更新者')),
            ],
            options={
                'permissions': (('can_approve', 'Can approve shop'),),
            },
        ),
        migrations.AddField(
            model_name='photo',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.Shop'),
        ),
        migrations.AddField(
            model_name='employment',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.Shop'),
        ),
        migrations.AddField(
            model_name='employment',
            name='staff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='belongs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contact',
            name='contact_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shops.ContactType', verbose_name='連絡方法'),
        ),
        migrations.AddField(
            model_name='contact',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.Shop'),
        ),
        migrations.AddField(
            model_name='benefit',
            name='shop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.Shop'),
        ),
    ]
