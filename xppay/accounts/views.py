from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.shortcuts import render
from django.views.generic.edit import UpdateView

from .forms import UserForm
from .models import User


@login_required
def index(request):
    return render(request, 'accounts/index.html')


class UserDetail(UpdateView):
    model = User
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        initial['perm_approval'] = self.request.user.has_perm('shops.can_approve')
        return initial

    def form_valid(self, form):
        user = self.request.user
        permission = Permission.objects.get(codename='can_approve')
        if form.cleaned_data.get('perm_approval') == 'True':
            if not user.has_perm('shops.can_approve'):
                user.user_permissions.add(permission)
        elif user.has_perm('shops.can_approve'):
            user.user_permissions.remove(permission)
        return super().form_valid(form)
