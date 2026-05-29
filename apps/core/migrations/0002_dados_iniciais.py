"""
Migration de dados iniciais.

Cria:
  - 10 usuarios Gestor (um por evento)
  - 10 Organizacoes (uma por organizador dos eventos)
  - 10 usuarios Organizador (um por organizacao, adicionado como membro)
  - 10 Eventos com os dados fornecidos
"""

import datetime
import shutil
import uuid
from pathlib import Path

from django.db import migrations


# ---------------------------------------------------------------------------
# Dados dos eventos (adaptados ao novo modelo)
# data_realizacao = datetime combinando data + horario originais
# local incorporado ao inicio da descricao
# ---------------------------------------------------------------------------
EVENTOS = [
    {
        "titulo": "Campeonato Universitario de Futebol",
        "foto": "eventos/futebol.jpg",
        "data_realizacao": datetime.datetime(2026, 6, 10, 9, 0),
        "organizador_nome": "Liga Atletica UnB",
        "gestor_nome": "Carlos Mendes",
        "descricao": (
            "Local: Campo de Futebol da UnB - Gramado Principal. "
            "Campeonato de futebol society entre os cursos da UnB. "
            "As equipes disputam fase de grupos e eliminatorias. "
            "Inscricoes por curso, minimo 7 jogadores."
        ),
    },
    {
        "titulo": "Torneio Interturmas de Volei",
        "foto": "eventos/volei.jpg",
        "data_realizacao": datetime.datetime(2026, 6, 17, 14, 0),
        "organizador_nome": "Centro Academico de Educacao Fisica",
        "gestor_nome": "Ana Paula Rocha",
        "descricao": (
            "Local: Ginasio Poliesportivo da FEF. "
            "Torneio interno de volei para alunos de todos os semestres. "
            "Modalidades masculino, feminino e misto."
        ),
    },
    {
        "titulo": "Corrida Universitaria 5K",
        "foto": "eventos/corrida.jpg",
        "data_realizacao": datetime.datetime(2026, 6, 22, 7, 0),
        "organizador_nome": "Atletica UnB Runners",
        "gestor_nome": "Fernanda Lima",
        "descricao": (
            "Local: Parque da Cidade - Portico Sul. "
            "Corrida de rua de 5 km com percurso dentro do Parque da Cidade. "
            "Aberta para alunos, professores e servidores."
        ),
    },
    {
        "titulo": "Festival de Natacao SIGEsporte",
        "foto": "eventos/natacao.jpg",
        "data_realizacao": datetime.datetime(2026, 7, 5, 8, 0),
        "organizador_nome": "Setor de Esportes Aquaticos",
        "gestor_nome": "Roberto Aquino",
        "descricao": (
            "Local: Piscina Olimpica da UnB. "
            "Festival interno de natacao com provas de 50m, 100m e 200m. "
            "Tambem havera revezamento 4x50m."
        ),
    },
    {
        "titulo": "Campeonato de Basquete 3x3",
        "foto": "eventos/basquete.jpg",
        "data_realizacao": datetime.datetime(2026, 7, 12, 10, 0),
        "organizador_nome": "Atletica de Engenharia",
        "gestor_nome": "Thiago Neves",
        "descricao": (
            "Local: Quadra de Basquete da Engenharia. "
            "Campeonato de basquete no formato 3x3 entre equipes mistas dos departamentos. "
            "Fase de grupos e mata-mata."
        ),
    },
    {
        "titulo": "Open de Tenis de Mesa",
        "foto": "eventos/tenis.jpg",
        "data_realizacao": datetime.datetime(2026, 7, 19, 13, 0),
        "organizador_nome": "Clube de Tenis de Mesa UnB",
        "gestor_nome": "Mariana Costa",
        "descricao": (
            "Local: Sala de Jogos do CCA. "
            "Torneio aberto de tenis de mesa para toda a comunidade universitaria. "
            "Formato eliminacao dupla."
        ),
    },
    {
        "titulo": "Torneio de Futsal Feminino",
        "foto": "eventos/futsal.jpg",
        "data_realizacao": datetime.datetime(2026, 8, 2, 15, 0),
        "organizador_nome": "Coletivo Esportivo Feminino UnB",
        "gestor_nome": "Juliana Ferreira",
        "descricao": (
            "Local: Ginasio Nilson Nelson - Quadra Auxiliar. "
            "Torneio exclusivo para equipes femininas de futsal formadas por estudantes. "
            "Arbitros credenciados pela CBFS."
        ),
    },
    {
        "titulo": "Circuito de Judo Universitario",
        "foto": "eventos/judo.jpg",
        "data_realizacao": datetime.datetime(2026, 8, 9, 9, 30),
        "organizador_nome": "Federacao Universitaria de Judo do DF",
        "gestor_nome": "Paulo Yamada",
        "descricao": (
            "Local: Dojo da FEF - Pavilhao de Lutas. "
            "Etapa universitaria do Circuito Regional de Judo. "
            "Categorias por peso seguindo tabela da CBJ."
        ),
    },
    {
        "titulo": "Maratona de Ciclismo Campus UnB",
        "foto": "eventos/ciclismo.jpg",
        "data_realizacao": datetime.datetime(2026, 8, 23, 6, 30),
        "organizador_nome": "Pedal UnB",
        "gestor_nome": "Diego Albuquerque",
        "descricao": (
            "Local: Estacionamento Central da UnB - Partida e Chegada. "
            "Percurso de 30 km pelo campus. "
            "Categorias speed, mountain bike e casual. Uso de capacete obrigatorio."
        ),
    },
    {
        "titulo": "Copa de Handebol Inter-Departamentos",
        "foto": "eventos/handebol.jpg",
        "data_realizacao": datetime.datetime(2026, 9, 6, 10, 0),
        "organizador_nome": "Departamento de Educacao Fisica",
        "gestor_nome": "Sandra Oliveira",
        "descricao": (
            "Local: Quadra Poliesportiva do ICC Norte. "
            "Copa de handebol entre os departamentos. "
            "Modalidades masculino e misto. Partidas de dois tempos de 25 minutos."
        ),
    },
]


def _slug(nome):
    """Gera username simples a partir de um nome (sem deps externas)."""
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", nome)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_str.lower().replace(" ", "_").replace("-", "_")[:40]


def _copiar_midias():
    """Copia imagens de static/media para media (MEDIA_ROOT)."""
    from django.conf import settings

    src = Path(settings.BASE_DIR) / "static" / "media" / "eventos"
    dst = Path(settings.MEDIA_ROOT) / "eventos"
    if src.exists():
        dst.mkdir(parents=True, exist_ok=True)
        for arquivo in src.iterdir():
            destino = dst / arquivo.name
            if not destino.exists():
                shutil.copy2(arquivo, destino)


def criar_dados(apps, schema_editor):
    _copiar_midias()

    Usuario = apps.get_model("security", "Usuario")
    Organizacao = apps.get_model("core", "Organizacao")
    Evento = apps.get_model("core", "Evento")

    for ev in EVENTOS:
        org_nome = ev["organizador_nome"]
        gestor_nome = ev["gestor_nome"]

        # 1. Criar/obter usuario Gestor (tipo GE)
        gestor_username = "gestor_" + _slug(gestor_nome)
        gestor, _ = Usuario.objects.get_or_create(
            username=gestor_username,
            defaults={
                "id": uuid.uuid4(),
                "email": gestor_username + "@sigesporte.unb.br",
                "nome_completo": gestor_nome,
                "tipo": "GE",
                "is_active": True,
                "password": "!unusable",
            },
        )

        # 2. Criar/obter Organizacao
        org, _ = Organizacao.objects.get_or_create(
            nome=org_nome,
            defaults={
                "id": uuid.uuid4(),
                "descricao": "Organizacao responsavel pelos eventos da " + org_nome + ".",
            },
        )

        # 3. Criar/obter usuario Organizador (tipo OR) e vincular a org
        org_username = "org_" + _slug(org_nome)
        organizador, _ = Usuario.objects.get_or_create(
            username=org_username,
            defaults={
                "id": uuid.uuid4(),
                "email": org_username + "@sigesporte.unb.br",
                "nome_completo": org_nome,
                "tipo": "OR",
                "is_active": True,
                "password": "!unusable",
            },
        )
        org.membros.add(organizador)

        # 4. Criar Evento
        Evento.objects.get_or_create(
            titulo=ev["titulo"],
            defaults={
                "id": uuid.uuid4(),                
                "foto": ev["foto"],
                "descricao": ev["descricao"],
                "data_realizacao": ev["data_realizacao"],
                "organizador": organizador,
                "organizacao": org,
            },
        )


def remover_dados(apps, schema_editor):
    Evento = apps.get_model("core", "Evento")
    Organizacao = apps.get_model("core", "Organizacao")
    Usuario = apps.get_model("security", "Usuario")

    titulos = [e["titulo"] for e in EVENTOS]
    Evento.objects.filter(titulo__in=titulos).delete()

    org_nomes = list({e["organizador_nome"] for e in EVENTOS})
    Organizacao.objects.filter(nome__in=org_nomes).delete()

    usernames = (
        ["gestor_" + _slug(e["gestor_nome"]) for e in EVENTOS]
        + ["org_" + _slug(e["organizador_nome"]) for e in EVENTOS]
    )
    Usuario.objects.filter(username__in=usernames).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        ("security", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_dados, remover_dados),
    ]
