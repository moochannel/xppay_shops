from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import Thumbnail

from shops.utils import make_qrcode_for_pdf


class Area(models.Model):
    name = models.CharField(max_length=20)
    list_order = models.IntegerField()

    def __str__(self):
        return self.name


class ActiveShopManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            models.Q(approvals__approved=ShopApproval.APPROVED),
            models.Q(approvals__canceled_at__isnull=True)
        )


class Shop(models.Model):
    area = models.ForeignKey(
        Area, verbose_name='地域', on_delete=models.PROTECT, related_name='shops'
    )
    name = models.CharField(verbose_name='店舗名', max_length=200)
    business_description = models.CharField(verbose_name='紹介文', max_length=1000)
    zipcode = models.CharField(
        verbose_name='郵便番号', max_length=7, help_text='ハイフンを入れず7桁の数字で入力してください'
    )
    address1 = models.CharField(verbose_name='住所1', max_length=100)
    address2 = models.CharField(verbose_name='住所2', max_length=100, blank=True)
    map_url = models.URLField(verbose_name='店舗地図URL', max_length=2000, blank=True)
    slug = models.SlugField(
        verbose_name='スラッグ',
        allow_unicode=True,
        default='',
        unique=True,
        help_text='URLで店舗を識別するための単語を指定します'
    )
    discord_for_payment = models.CharField(
        verbose_name='支払先Discordアカウント',
        max_length=100,
        default='@',
        help_text='XPpayでの支払先に使用するDiscordアカウント名を指定します'
    )
    in_qrcode = models.CharField(
        verbose_name='QRコード用文字列',
        max_length=2000,
        blank=True,
        help_text='PDF内に表示するQRコードに埋め込む文字列を指定します'
    )
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    created_by = models.ForeignKey(
        User, verbose_name='作成者', on_delete=models.PROTECT, related_name='shop_creator'
    )
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    updated_by = models.ForeignKey(
        User, verbose_name='更新者', on_delete=models.PROTECT, related_name='shop_updater'
    )

    objects = models.Manager()
    active_objects = ActiveShopManager()

    def get_absolute_url(self):
        return reverse('shops:shop_detail', kwargs={'slug': self.slug})

    def benefits_available(self, when=None):
        if when:
            basis_dt = when
            if timezone.is_naive(when):
                basis_dt = timezone.make_aware(basis_dt, timezone.get_current_timezone())
        else:
            basis_dt = timezone.now()

        return self.benefit_set.filter(
            models.Q(starts_at__lte=basis_dt),
            (models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=basis_dt))
        ).order_by('-ends_at', '-starts_at')

    def qrcode_b64(self):
        return make_qrcode_for_pdf(self.in_qrcode)


class WaitForApprovalManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            models.Q(approved__in=[ShopApproval.REQUESTED, ShopApproval.EXAMINE]),
            models.Q(canceled_at__isnull=True)
        )


class ShopApproval(models.Model):
    REQUESTED = 'RE'
    EXAMINE = 'EX'
    APPROVED = 'AP'
    DENIED = 'DE'
    APPROVAL_CHOICES = (
        (REQUESTED, '申請済み'),
        (EXAMINE, '審査中'),
        (APPROVED, '承認'),
        (DENIED, '否認'),
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='approvals')
    requested_at = models.DateTimeField(verbose_name='申請日時', auto_now_add=True)
    requested_by = models.ForeignKey(
        User, verbose_name='申請者', on_delete=models.PROTECT, related_name='request_approvals'
    )
    canceled_at = models.DateTimeField(verbose_name='取り下げ・取消日時', null=True)
    canceled_by = models.ForeignKey(
        User,
        verbose_name='取消者',
        null=True,
        on_delete=models.PROTECT,
        related_name='canceled_approvals'
    )
    approved = models.CharField(
        verbose_name='承認結果', max_length=2, choices=APPROVAL_CHOICES, default=REQUESTED
    )
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)
    updated_by = models.ForeignKey(
        User, verbose_name='更新者', on_delete=models.PROTECT, related_name='update_approvals'
    )

    objects = models.Manager()
    waiting_objects = WaitForApprovalManager()

    def stats(self):
        if self.canceled_at:
            return '取り下げ'
        else:
            return self.get_approved_display()


class ContactType(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Contact(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    list_order = models.IntegerField(verbose_name='表示優先順', help_text='数値の低い方が優先されます')
    contact_type = models.ForeignKey(ContactType, on_delete=models.PROTECT, verbose_name='連絡方法')
    label = models.CharField(verbose_name='表示名', max_length=100)
    href = models.CharField(verbose_name='リンク', max_length=300, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('shops:contact_list', kwargs={'slug': self.shop.slug})


class Benefit(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    content = models.CharField(verbose_name='特典内容', max_length=200)
    starts_at = models.DateTimeField(verbose_name='開始日時', default=timezone.now)
    ends_at = models.DateTimeField(verbose_name='終了日時', blank=True, null=True)

    STATE_CHOICES = (
        (1, '利用可能'),
        (0, '予定'),
        (-1, '終了済み'),
    )

    def get_absolute_url(self):
        return reverse('shops:benefit_list', kwargs={'slug': self.shop.slug})

    @classmethod
    def get_state_display(cls, state):
        for choice_id, choice_label in cls.STATE_CHOICES:
            if choice_id == state:
                return choice_label

        return None


class Photo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    origin = models.ImageField(
        verbose_name='店舗画像',
        upload_to='shops/origin/%y/%m/%d',
        help_text='PCでは画像ファイルをファイルボタンにドラッグすると簡単に指定できます'
    )
    carousel = ImageSpecField(
        source='origin', processors=[Thumbnail(840, 440)], options={
            'quality': 85
        }
    )
    thumbnail = ImageSpecField(
        source='origin', processors=[Thumbnail(210, 110)], options={
            'quality': 80
        }
    )

    class Meta:
        ordering = ['pk']

    def get_absolute_url(self):
        return reverse('shops:photo_list', kwargs={'slug': self.shop.slug})

    def delete(self, *args, **kwargs):
        storage = self.origin.storage
        path = self.origin.path
        super().delete(*args, **kwargs)
        try:
            storage.delete(path)
        except BaseException:
            print(f'error occured on delete origin file: {path}')
            raise
