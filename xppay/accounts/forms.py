from django import forms
import material

from .models import User


class UserForm(forms.ModelForm):
    perm_approval = forms.ChoiceField(
        label='承認権限', choices=((False, 'なし'), (True, 'あり')), widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ['username']

    layout = material.Layout(
        material.Row('username'), material.Fieldset('デモ版限定機能', material.Row('perm_approval'))
    )
