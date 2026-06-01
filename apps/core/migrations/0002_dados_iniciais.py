"""
apps.core.migrations.0001_initial
===================================
Migration inicial do domínio de Eventos.

Cria a tabela ``core_evento`` com todos os campos do modelo
:class:`~apps.core.models.eventos_models.Evento`.

Notas
-----
- Requer Python >= 3.12
- Criado por `Gui-fga <https://github.com/Gui-fga>`_ em 30 maio 2026
- Revisado por `Saresu <https://github.com/Saresu>`_ em 30 maio 2026
"""

# suprimindo invalid name
# pylint: disable=invalid-name

import datetime

from django.db import migrations


__version__ = "0.0.1"
__license__ = "AGPL V3"


EVENTOS_INICIAIS = [
    {
        "nome": "Campeonato Universitario de Futebol",
        "data": datetime.date(2026, 6, 10),
        "horario": datetime.time(9, 0),
        "local": "Campo de Futebol da UnB - Gramado Principal",
        "organizador": "Liga Atletica UnB",
        "gestor": "Carlos Mendes",
        "descricao": "Campeonato de futebol society entre os cursos da UnB. "
        "As equipes disputam fase de grupos e eliminatorias."
        " Inscricoes por curso, minimo 7 jogadores.",
        "capacidade": 500,
    },
    {
        "nome": "Torneio Interturmas de Volei",
        "data": datetime.date(2026, 6, 17),
        "horario": datetime.time(14, 0),
        "local": "Ginasio Poliesportivo da FEF",
        "organizador": "Centro Academico de Educacao Fisica",
        "gestor": "Ana Paula Rocha",
        "descricao": "Torneio interno de volei para alunos de todos os semestres."
        " Modalidades masculino, feminino e misto.",
        "capacidade": 300,
    },
    {
        "nome": "Corrida Universitaria 5K",
        "data": datetime.date(2026, 6, 22),
        "horario": datetime.time(7, 0),
        "local": "Parque da Cidade - Portico Sul",
        "organizador": "Atletica UnB Runners",
        "gestor": "Fernanda Lima",
        "descricao": "Corrida de rua de 5 km com percurso dentro do Parque da Cidade."
        " Aberta para alunos, professores e servidores.",
        "capacidade": 400,
    },
    {
        "nome": "Festival de Natacao SIGEsporte",
        "data": datetime.date(2026, 7, 5),
        "horario": datetime.time(8, 0),
        "local": "Piscina Olimpica da UnB",
        "organizador": "Setor de Esportes Aquaticos",
        "gestor": "Roberto Aquino",
        "descricao": "Festival interno de natacao com provas de 50m, 100m e 200m."
        " Tambem havera revezamento 4x50m.",
        "capacidade": 200,
    },
    {
        "nome": "Campeonato de Basquete 3x3",
        "data": datetime.date(2026, 7, 12),
        "horario": datetime.time(10, 0),
        "local": "Quadra de Basquete da Engenharia",
        "organizador": "Atletica de Engenharia",
        "gestor": "Thiago Neves",
        "descricao": "Campeonato de basquete no formato 3x3 entre equipes mistas dos departamentos."
        " Fase de grupos e mata-mata.",
        "capacidade": 250,
    },
    {
        "nome": "Open de Tenis de Mesa",
        "data": datetime.date(2026, 7, 19),
        "horario": datetime.time(13, 0),
        "local": "Sala de Jogos do CCA",
        "organizador": "Clube de Tenis de Mesa UnB",
        "gestor": "Mariana Costa",
        "descricao": "Torneio aberto de tenis de mesa para toda a comunidade universitaria."
        " Formato eliminacao dupla.",
        "capacidade": 80,
    },
    {
        "nome": "Torneio de Futsal Feminino",
        "data": datetime.date(2026, 8, 2),
        "horario": datetime.time(15, 0),
        "local": "Ginasio Nilson Nelson - Quadra Auxiliar",
        "organizador": "Coletivo Esportivo Feminino UnB",
        "gestor": "Juliana Ferreira",
        "descricao": "Torneio exclusivo para equipes femininas de futsal formadas por estudantes."
        " Arbitros credenciados pela CBFS.",
        "capacidade": 350,
    },
    {
        "nome": "Circuito de Judo Universitario",
        "data": datetime.date(2026, 8, 9),
        "horario": datetime.time(9, 30),
        "local": "Dojo da FEF - Pavilhao de Lutas",
        "organizador": "Federacao Universitaria de Judo do DF",
        "gestor": "Paulo Yamada",
        "imagem": "eventos/judo.jpg",
        "descricao": "Etapa universitaria do Circuito Regional de Judo."
        " Categorias por peso seguindo tabela da CBJ.",
        "capacidade": 150,
    },
    {
        "nome": "Maratona de Ciclismo Campus UnB",
        "data": datetime.date(2026, 8, 23),
        "horario": datetime.time(6, 30),
        "local": "Estacionamento Central da UnB - Partida e Chegada",
        "organizador": "Pedal UnB",
        "gestor": "Diego Albuquerque",
        "descricao": "Percurso de 30 km pelo campus."
        " Categorias speed, mountain bike e casual. Uso de capacete obrigatorio.",
        "capacidade": 180,
    },
    {
        "nome": "Copa de Handebol Inter-Departamentos",
        "data": datetime.date(2026, 9, 6),
        "horario": datetime.time(10, 0),
        "local": "Quadra Poliesportiva do ICC Norte",
        "organizador": "Departamento de Educacao Fisica",
        "gestor": "Sandra Oliveira",
        "descricao": "Copa de handebol entre os departamentos."
        " Modalidades masculino e misto."
        " Partidas de dois tempos de 25 minutos.",
        "capacidade": 280,
    },
]

# revertento a logica precisa do positional
# por bom senso suprimindo o lint no argumento nao usado
def inserir_eventos(apps, schema_editor): # pylint: disable=unused-argument
    """Migration inicial que cria o modelo Evento no banco de dados."""

    Evento = apps.get_model("core", "Evento")
    for dados in EVENTOS_INICIAIS:
        Evento.objects.create(**dados)


# def remover_eventos(apps): # suprimindo para passar no lint, schema_editor):
# revertento a logica precisa do positional
def remover_eventos(apps, schema_editor): # pylint: disable=unused-argument
    """Remove os eventos iniciais do banco de dados."""

    Evento = apps.get_model("core", "Evento")
    nomes = [e["nome"] for e in EVENTOS_INICIAIS]
    Evento.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):
    """Migration que popula o banco com eventos esportivos universitários iniciais."""

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(inserir_eventos, reverse_code=remover_eventos),
    ]
