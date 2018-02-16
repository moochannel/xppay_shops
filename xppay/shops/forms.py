import material
from django import forms

from .models import Benefit, Contact, Employment, Photo, Shop, ShopApproval


class ShopForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = [
            'area', 'name', 'slug', 'discord_for_payment', 'business_description', 'zipcode',
            'address1', 'address2', 'map_url'
        ]
        widgets = {
            'business_description': forms.Textarea(attrs={
                'rows': 5
            }),
        }


class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['list_order', 'contact_type', 'label', 'href']


class BenefitForm(forms.ModelForm):

    class Meta:
        model = Benefit
        fields = ['starts_at', 'ends_at', 'content']

    layout = material.Layout(
        material.Row('starts_at', 'ends_at'),
        material.Row('content'),
    )


class BenefitCancelForm(forms.ModelForm):

    class Meta:
        model = Benefit
        fields = []


class PhotoForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['origin']

    layout = material.Layout(material.Row('origin'),)


class ShopApproveRequestForm(forms.ModelForm):

    class Meta:
        model = ShopApproval
        fields = []


class ShopApproveForm(forms.ModelForm):

    class Meta:
        model = ShopApproval
        fields = ['approved', 'in_qrcode']

    def clean(self):
        cleaned_data = super().clean()
        if (cleaned_data.get('approved') == ShopApproval.APPROVED and
                not (cleaned_data.get('in_qrcode'))):
            self.add_error('in_qrcode', '承認を選ぶ場合はQRコード用文字列を入力してください')


class StaffForm(forms.ModelForm):

    class Meta:
        model = Employment
        fields = ['staff']

    layout = material.Layout(material.Fieldset('スタッフ追加', material.Row('staff')),)
