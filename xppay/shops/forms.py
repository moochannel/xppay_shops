import material
from django import forms

from .models import Benefit, Photo, Shop


class ShopForm(forms.ModelForm):

    class Meta:
        model = Shop
        fields = [
            'area', 'name', 'business_description', 'zipcode', 'address1', 'address2', 'map_url'
        ]
        widgets = {
            'business_description': forms.Textarea(attrs={
                'rows': 5
            }),
        }


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
        fields = ['origin', 'list_order']

    layout = material.Layout(
        material.Row('origin'),
        material.Row('list_order'),
    )
