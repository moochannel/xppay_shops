import material
from django import forms

from .models import Benefit, Contact, Photo, Shop, ShopApproval


class ShopForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = [
            'area', 'name', 'slug', 'discord_for_payment', 'business_description', 'zipcode',
            'address1', 'address2', 'map_url', 'in_qrcode'
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


class PhotoForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['origin']

    layout = material.Layout(material.Row('origin'),)


class ShopApproveRequestForm(forms.ModelForm):

    class Meta:
        model = ShopApproval
        fields = []
