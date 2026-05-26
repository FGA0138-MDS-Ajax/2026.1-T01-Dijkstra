from django.db import models

class Evento(models.Model):
    """
    Representa um evento no sistema SIGEsporte.
    """

    nome = models.CharField(
        max_length=100,
        verbose_name="Nome do Evento"
    )

    data = models.DateField(
        verbose_name="Data do Evento"
    )

    horario = models.TimeField(
        verbose_name="Horário do Evento"
    )

    local = models.CharField(
        max_length=150,
        verbose_name="Local"
    )

    organizador = models.CharField(
        max_length=100,
        verbose_name="Organizador"
    )

    gestor = models.CharField(
        max_length=100,
        verbose_name="Gestor"
    )

    descricao = models.TextField(
        verbose_name="Descrição",
        blank=True,
        null=True
    )

    capacidade = models.PositiveIntegerField(
        verbose_name="Capacidade de Pessoas"
    )

    imagem = models.ImageField(
        upload_to='eventos/',
        verbose_name="Imagem do Evento",
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-data', '-horario']

    def __str__(self):
        return self.nome
