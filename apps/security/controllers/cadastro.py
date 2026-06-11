from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def cadastro(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        matricula = request.POST.get("matricula")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get("confirmar_senha")

        if senha != confirmar_senha:
            return render(
                request,
                "security/cadastro.html",
                {"erro": "As senhas não coincidem."},
            )

        if User.objects.filter(username=matricula).exists():
            return render(
                request,
                "security/cadastro.html",
                {"erro": "Matrícula já cadastrada."},
            )

        User.objects.create_user(
            username=matricula,
            first_name=nome,
            password=senha,
        )

        return redirect("login")

    return render(request, "security/cadastro.html")