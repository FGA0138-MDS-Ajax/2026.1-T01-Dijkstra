from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do Evento')),
                ('data', models.DateField(verbose_name='Data do Evento')),
                ('horario', models.TimeField(verbose_name='Horario do Evento')),
                ('local', models.CharField(max_length=150, verbose_name='Local')),
                ('organizador', models.CharField(max_length=100, verbose_name='Organizador')),
                ('gestor', models.CharField(max_length=100, verbose_name='Gestor')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descricao')),
                ('capacidade', models.PositiveIntegerField(verbose_name='Capacidade de Pessoas')),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='eventos/', verbose_name='Imagem do Evento')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Evento',
                'verbose_name_plural': 'Eventos',
                'ordering': ['-data', '-horario'],
            },
        ),
    ]
