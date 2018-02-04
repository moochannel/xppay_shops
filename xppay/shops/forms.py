from django import forms

from .models import Shop


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
