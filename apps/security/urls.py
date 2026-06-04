"""Mapeamento de URLs do app."""

from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    # Rota de Login
    path('login/', auth_views.LoginView.as_view(template_name='security/login.html'), name='login'),
    # Rota de Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # Rota temporária de Cadastro (Apenas para não dar erro no botão)
    path('cadastro/', TemplateView.as_view(template_name='security/cadastro.html'), name='cadastro'),
    # Rota de recuperação de senha
    path('esqueci-senha/', TemplateView.as_view(template_name='security/esqueceu_senha.html'), name='esqueceu_senha'),
]
