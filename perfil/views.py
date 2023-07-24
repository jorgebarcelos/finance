from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages
from django.db.models import Sum
from extrato.models import Valores
from .models import Conta, Categoria
from .utils import calcula_total

# Create your views here.


def home(request):
    contas = Conta.objects.all()
    total_contas = calcula_total(contas, 'valor')

    return render(request, "home.html", {'contas': contas, 'total_contas': total_contas})


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = calcula_total(contas, 'valor')

    return render(request, "gerenciar.html", {"contas": contas, "total_contas": total_contas, 'categorias': categorias})


def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')

    conta = Conta(apelido=apelido, banco=banco, tipo=tipo, valor=valor, icone=icone)
    conta.save()

    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')
    return redirect('/perfil/gerenciar/')


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso!')
    return redirect('/perfil/gerenciar/')


def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(categoria=nome, essencial=essencial)

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()

    return redirect('/perfil/gerenciar/')


def dashboard(request):
    titulo = 'Gastos por categoria'
    dados = {}
    categorias = Categoria.objects.all()
    mes_atual = datetime.now().month

    for categoria in categorias:
        valores = (
            Valores.objects.filter(tipo='S')
            .filter(data__month=mes_atual)
            .filter(categoria=categoria)
            .aggregate(Sum('valor'))['valor__sum']
        )
        valores = valores if valores is not None else 0
        dados[categoria.categoria] = valores

    return render(
        request, 'dashboard.html', {'titulo': titulo, 'labels': list(dados.keys()), 'values': list(dados.values())}
    )
