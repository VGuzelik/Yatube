from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    # функция reverse_lazy выполняет построение маршрута только в момент,
    # когда он понадобится.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
