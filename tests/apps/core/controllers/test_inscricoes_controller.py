"""Testes para o controller de gestão de inscrições.

tests.apps.core.controllers.test_inscricoes_controller
=======================================================
Cobre as views:
- gestao_inscricoes
- aprovar_inscricao
- reprovar_inscricao
- aprovar_todas_pendentes
- exportar_inscricoes_csv
"""

from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.core.models.eventos_models import Evento
from apps.core.models.inscricao_models import Inscricao
from apps.core.models.organizacoes_models import Organizacao

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixture compartilhada
# ---------------------------------------------------------------------------

class BaseInscricoesTest(TestCase):
    """Configura os objetos comuns a todos os grupos de teste."""

    def setUp(self):
        self.client = Client()

        # Organizador — tem acesso às views de gestão
        self.organizador = User.objects.create_user(
            username="organizador",
            password="senha123",
            tipo="OR",
            nome_completo="Organizador Teste",
            matricula="111111111",
        )

        # Aluno — candidato a inscrição
        self.aluno = User.objects.create_user(
            username="aluno",
            password="senha123",
            tipo="AL",
            nome_completo="Aluno Teste",
            matricula="222222222",
        )

        # Gestor — não deve ter acesso às views de organizador
        self.gestor = User.objects.create_user(
            username="gestor",
            password="senha123",
            tipo="GE",
            nome_completo="Gestor Teste",
        )

        self.organizacao = Organizacao.objects.create(
            nome="Organização Inscrições", descricao="Org de teste.",
        )

        self.evento = Evento.objects.create(
            nome="Torneio de Xadrez",
            data=date(2026, 9, 15),
            horario=time(10, 0),
            local="Auditório FGA",
            organizador=self.organizador,
            organizacao=self.organizacao,
            descricao="Evento de xadrez universitário",
            capacidade=30,
            status=Evento.Status.PUBLICADO,
        )

        self.inscricao_pendente = Inscricao.objects.create(
            aluno=self.aluno,
            evento=self.evento,
            status=Inscricao.Status.PENDENTE,
        )

    def _login_organizador(self):
        self.client.force_login(self.organizador)

    def _login_aluno(self):
        self.client.force_login(self.aluno)

    def _login_gestor(self):
        self.client.force_login(self.gestor)

    def _url_gestao(self):
        return reverse("gestao-inscricoes", kwargs={"evento_id": self.evento.id})

    def _url_aprovar(self, inscricao=None):
        inscricao = inscricao or self.inscricao_pendente
        return reverse("aprovar-inscricao", kwargs={"inscricao_id": inscricao.id})

    def _url_reprovar(self, inscricao=None):
        inscricao = inscricao or self.inscricao_pendente
        return reverse("reprovar-inscricao", kwargs={"inscricao_id": inscricao.id})

    def _url_aprovar_todos(self):
        return reverse("aprovar-todos-inscritos", kwargs={"evento_id": self.evento.id})

    def _url_exportar_csv(self):
        return reverse("exportar-inscricoes-csv", kwargs={"evento_id": self.evento.id})


# ---------------------------------------------------------------------------
# gestao_inscricoes
# ---------------------------------------------------------------------------

class GestaoInscricoesAcessoTest(BaseInscricoesTest):
    """Controle de acesso à página de gestão de inscritos."""

    def test_organizador_acessa_com_sucesso(self):
        self._login_organizador()
        response = self.client.get(self._url_gestao())
        self.assertEqual(response.status_code, 200)

    def test_nao_autenticado_redireciona(self):
        response = self.client.get(self._url_gestao())
        self.assertIn(response.status_code, [302, 403])

    def test_aluno_recebe_403(self):
        self._login_aluno()
        response = self.client.get(self._url_gestao())
        self.assertEqual(response.status_code, 403)

    def test_gestor_recebe_403(self):
        self._login_gestor()
        response = self.client.get(self._url_gestao())
        self.assertEqual(response.status_code, 403)

    def test_evento_inexistente_retorna_404(self):
        from uuid import uuid4
        self._login_organizador()
        url = reverse("gestao-inscricoes", kwargs={"evento_id": uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class GestaoInscricoesConteudoTest(BaseInscricoesTest):
    """Conteúdo e contexto da página de gestão de inscritos."""

    def setUp(self):
        super().setUp()
        self._login_organizador()

    def test_usa_template_correto(self):
        response = self.client.get(self._url_gestao())
        self.assertTemplateUsed(response, "core/inscricoes/gestao_inscricoes.html")

    def test_contexto_contem_evento(self):
        response = self.client.get(self._url_gestao())
        self.assertEqual(response.context["evento"].id, self.evento.id)

    def test_contexto_contem_contadores(self):
        response = self.client.get(self._url_gestao())
        self.assertEqual(response.context["total"], 1)
        self.assertEqual(response.context["pendentes"], 1)
        self.assertEqual(response.context["aprovadas"], 0)
        self.assertEqual(response.context["rejeitadas"], 0)

    def test_inscricao_aparece_na_listagem(self):
        response = self.client.get(self._url_gestao())
        matriculas = [i.aluno.matricula for i in response.context["page_obj"].object_list]
        self.assertIn(self.aluno.matricula, matriculas)

    def test_filtro_por_status_pendente(self):
        Inscricao.objects.create(
            aluno=self.organizador,
            evento=self.evento,
            status=Inscricao.Status.APROVADA,
        )
        response = self.client.get(self._url_gestao(), {"status": "pendente"})
        page_obj = response.context["page_obj"]
        self.assertTrue(all(i.status == Inscricao.Status.PENDENTE for i in page_obj))

    def test_filtro_por_status_aprovada(self):
        self.inscricao_pendente.status = Inscricao.Status.APROVADA
        self.inscricao_pendente.save()
        response = self.client.get(self._url_gestao(), {"status": "aprovada"})
        page_obj = response.context["page_obj"]
        self.assertTrue(all(i.status == Inscricao.Status.APROVADA for i in page_obj))

    def test_status_filtro_invalido_retorna_todos(self):
        response = self.client.get(self._url_gestao(), {"status": "naoexiste"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_paginacao_15_por_pagina(self):
        # Cria 20 alunos adicionais e os inscreve
        for i in range(20):
            aluno = User.objects.create_user(
                username=f"aluno_extra_{i}",
                password="senha123",
                tipo="AL",
                nome_completo=f"Aluno Extra {i}",
            )
            Inscricao.objects.create(aluno=aluno, evento=self.evento)

        response = self.client.get(self._url_gestao())
        self.assertEqual(len(response.context["page_obj"].object_list), 15)

    def test_segunda_pagina_acessivel(self):
        for i in range(20):
            aluno = User.objects.create_user(
                username=f"aluno_p2_{i}",
                password="senha123",
                tipo="AL",
                nome_completo=f"Aluno P2 {i}",
            )
            Inscricao.objects.create(aluno=aluno, evento=self.evento)

        response = self.client.get(self._url_gestao(), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)


# ---------------------------------------------------------------------------
# aprovar_inscricao
# ---------------------------------------------------------------------------

class AprovarInscricaoTest(BaseInscricoesTest):
    """Aprovação individual de inscrição."""

    def test_organizador_aprova_inscricao_pendente(self):
        self._login_organizador()
        response = self.client.post(self._url_aprovar())

        self.assertRedirects(
            response,
            reverse("gestao-inscricoes", kwargs={"evento_id": self.evento.id}),
        )
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.APROVADA)

    def test_aprovacao_registra_avaliador(self):
        self._login_organizador()
        self.client.post(self._url_aprovar())
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.avaliador, self.organizador)

    def test_aprovacao_registra_data_avaliacao(self):
        self._login_organizador()
        self.client.post(self._url_aprovar())
        self.inscricao_pendente.refresh_from_db()
        self.assertIsNotNone(self.inscricao_pendente.data_avaliacao)

    def test_nao_aprova_inscricao_ja_aprovada(self):
        self.inscricao_pendente.status = Inscricao.Status.APROVADA
        self.inscricao_pendente.save()

        self._login_organizador()
        self.client.post(self._url_aprovar())

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.APROVADA)

    def test_nao_aprova_inscricao_rejeitada(self):
        self.inscricao_pendente.status = Inscricao.Status.REJEITADA
        self.inscricao_pendente.save()

        self._login_organizador()
        self.client.post(self._url_aprovar())

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.REJEITADA)

    def test_aluno_nao_pode_aprovar(self):
        self._login_aluno()
        response = self.client.post(self._url_aprovar())
        self.assertEqual(response.status_code, 403)
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.PENDENTE)

    def test_gestor_nao_pode_aprovar(self):
        self._login_gestor()
        response = self.client.post(self._url_aprovar())
        self.assertEqual(response.status_code, 403)

    def test_nao_autenticado_nao_pode_aprovar(self):
        response = self.client.post(self._url_aprovar())
        self.assertIn(response.status_code, [302, 403])
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.PENDENTE)


# ---------------------------------------------------------------------------
# reprovar_inscricao
# ---------------------------------------------------------------------------

class ReprovarInscricaoTest(BaseInscricoesTest):
    """Reprovação de inscrição com justificativa."""

    def test_organizador_reprova_com_motivo(self):
        self._login_organizador()
        response = self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Perfil incompatível com o evento."},
        )

        self.assertRedirects(
            response,
            reverse("gestao-inscricoes", kwargs={"evento_id": self.evento.id}),
        )
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.REJEITADA)

    def test_reprovacao_persiste_motivo(self):
        self._login_organizador()
        motivo = "Documentação pendente."
        self.client.post(self._url_reprovar(), {"motivo_reprovacao": motivo})
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.motivo_reprovacao, motivo)

    def test_reprovacao_registra_avaliador(self):
        self._login_organizador()
        self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Sem vagas para o perfil."},
        )
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.avaliador, self.organizador)

    def test_reprovacao_registra_data_avaliacao(self):
        self._login_organizador()
        self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Sem vagas para o perfil."},
        )
        self.inscricao_pendente.refresh_from_db()
        self.assertIsNotNone(self.inscricao_pendente.data_avaliacao)

    def test_reprovacao_sem_motivo_nao_muda_status(self):
        self._login_organizador()
        self.client.post(self._url_reprovar(), {"motivo_reprovacao": ""})
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.PENDENTE)

    def test_nao_reprova_inscricao_ja_aprovada(self):
        self.inscricao_pendente.status = Inscricao.Status.APROVADA
        self.inscricao_pendente.save()

        self._login_organizador()
        self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Erro."},
        )

        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.APROVADA)

    def test_aluno_nao_pode_reprovar(self):
        self._login_aluno()
        response = self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Tentativa indevida."},
        )
        self.assertEqual(response.status_code, 403)
        self.inscricao_pendente.refresh_from_db()
        self.assertEqual(self.inscricao_pendente.status, Inscricao.Status.PENDENTE)

    def test_gestor_nao_pode_reprovar(self):
        self._login_gestor()
        response = self.client.post(
            self._url_reprovar(),
            {"motivo_reprovacao": "Tentativa indevida."},
        )
        self.assertEqual(response.status_code, 403)


# ---------------------------------------------------------------------------
# aprovar_todas_pendentes
# ---------------------------------------------------------------------------

class AprovarTodasPendentesTest(BaseInscricoesTest):
    """Aprovação em lote de inscrições pendentes."""

    def _criar_inscricao(self, username, status=Inscricao.Status.PENDENTE):
        aluno = User.objects.create_user(
            username=username,
            password="senha123",
            tipo="AL",
            nome_completo=f"Aluno {username}",
        )
        return Inscricao.objects.create(aluno=aluno, evento=self.evento, status=status)

    def test_aprova_todas_as_pendentes(self):
        self._criar_inscricao("aluno2")
        self._criar_inscricao("aluno3")

        self._login_organizador()
        self.client.post(self._url_aprovar_todos())

        pendentes_restantes = Inscricao.objects.filter(
            evento=self.evento,
            status=Inscricao.Status.PENDENTE,
        ).count()
        self.assertEqual(pendentes_restantes, 0)

    def test_nao_afeta_inscricoes_ja_aprovadas(self):
        aprovada = self._criar_inscricao("aluno_ja_aprovado", status=Inscricao.Status.APROVADA)

        self._login_organizador()
        self.client.post(self._url_aprovar_todos())

        aprovada.refresh_from_db()
        # Continua aprovada (não foi regravada desnecessariamente)
        self.assertEqual(aprovada.status, Inscricao.Status.APROVADA)

    def test_nao_afeta_inscricoes_rejeitadas(self):
        rejeitada = self._criar_inscricao("aluno_rejeitado", status=Inscricao.Status.REJEITADA)

        self._login_organizador()
        self.client.post(self._url_aprovar_todos())

        rejeitada.refresh_from_db()
        self.assertEqual(rejeitada.status, Inscricao.Status.REJEITADA)

    def test_sem_pendentes_exibe_aviso(self):
        self.inscricao_pendente.status = Inscricao.Status.APROVADA
        self.inscricao_pendente.save()

        self._login_organizador()
        response = self.client.post(self._url_aprovar_todos(), follow=True)

        messages = [str(m) for m in response.context["messages"]]
        self.assertTrue(any("pendente" in m.lower() for m in messages))

    def test_redireciona_para_gestao_inscricoes(self):
        self._login_organizador()
        response = self.client.post(self._url_aprovar_todos())
        self.assertRedirects(
            response,
            reverse("gestao-inscricoes", kwargs={"evento_id": self.evento.id}),
        )

    def test_aluno_nao_pode_aprovar_em_lote(self):
        self._login_aluno()
        response = self.client.post(self._url_aprovar_todos())
        self.assertEqual(response.status_code, 403)

    def test_gestor_nao_pode_aprovar_em_lote(self):
        self._login_gestor()
        response = self.client.post(self._url_aprovar_todos())
        self.assertEqual(response.status_code, 403)

    def test_nao_autenticado_nao_pode_aprovar_em_lote(self):
        response = self.client.post(self._url_aprovar_todos())
        self.assertIn(response.status_code, [302, 403])

    def test_metodo_get_nao_e_permitido(self):
        self._login_organizador()
        response = self.client.get(self._url_aprovar_todos())
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# exportar_inscricoes_csv
# ---------------------------------------------------------------------------

class ExportarInscricoesCsvTest(BaseInscricoesTest):
    """Exportação da lista de inscritos em CSV."""

    def _get_csv(self):
        self._login_organizador()
        return self.client.get(self._url_exportar_csv())

    def test_retorna_200(self):
        response = self._get_csv()
        self.assertEqual(response.status_code, 200)

    def test_content_type_csv(self):
        response = self._get_csv()
        self.assertIn("text/csv", response["Content-Type"])

    def test_header_content_disposition(self):
        response = self._get_csv()
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".csv", response["Content-Disposition"])

    def test_cabecalho_csv_presente(self):
        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        self.assertIn("Nome", content)
        self.assertIn("Status", content)
        self.assertIn("Data da Solicitação", content)

    def test_dados_do_inscrito_presentes(self):
        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        # O nome completo (ou username como fallback) do aluno deve aparecer no CSV
        nome = self.aluno.get_full_name() or self.aluno.username
        self.assertIn(nome, content)

    def test_status_legivel_no_csv(self):
        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        self.assertIn("Pendente", content)

    def test_inscricao_aprovada_exportada_corretamente(self):
        self.inscricao_pendente.status = Inscricao.Status.APROVADA
        self.inscricao_pendente.avaliador = self.organizador
        self.inscricao_pendente.save()

        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        self.assertIn("Aprovada", content)

    def test_motivo_reprovacao_exportado(self):
        self.inscricao_pendente.status = Inscricao.Status.REJEITADA
        self.inscricao_pendente.motivo_reprovacao = "Sem vagas disponíveis."
        self.inscricao_pendente.avaliador = self.organizador
        self.inscricao_pendente.save()

        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        self.assertIn("Sem vagas disponíveis.", content)

    def test_aluno_nao_pode_exportar(self):
        self._login_aluno()
        response = self.client.get(self._url_exportar_csv())
        self.assertEqual(response.status_code, 403)

    def test_gestor_nao_pode_exportar(self):
        self._login_gestor()
        response = self.client.get(self._url_exportar_csv())
        self.assertEqual(response.status_code, 403)

    def test_nao_autenticado_nao_pode_exportar(self):
        response = self.client.get(self._url_exportar_csv())
        self.assertIn(response.status_code, [302, 403])

    def test_evento_sem_inscritos_gera_csv_apenas_com_cabecalho(self):
        self.inscricao_pendente.delete()
        response = self._get_csv()
        content = response.content.decode("utf-8-sig")
        linhas = [l for l in content.splitlines() if l.strip()]
        # Apenas a linha de cabeçalho
        self.assertEqual(len(linhas), 1)
