.PHONY: install run check migrate migrations shell test lint clear venv help

help:
	@echo "SIGEsporte — comandos disponíveis:"
	@echo ""
	@echo "  make venv        Cria o ambiente virtual em .venv"
	@echo "  make install     Instala as dependências do requirements.txt"
	@echo "  make run         Inicia o servidor de desenvolvimento"
	@echo "  make check       Valida a configuração do Django"
	@echo "  make migrations  Gera as migrations"
	@echo "  make migrate     Aplica as migrations no banco"
	@echo "  make shell       Abre o shell interativo do Django"
	@echo "  make test        Executa os testes com pytest"
	@echo "  make lint        Analisa o código com pylint"
	@echo "  make clear       Remove __pycache__, .pyc e o .venv"
	@echo "  make help        Exibe esta mensagem"

venv:
	python3 -m venv .venv
	@echo "Ative com: source .venv/bin/activate"

install:
	pip install -r requirements.txt

run:
	python3 manage.py runserver

check:
	python3 manage.py check

migrations:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

shell:
	python3 manage.py shell

test:
	pytest

lint:
	DJANGO_SETTINGS_MODULE=config.settings pylint --load-plugins pylint_django apps/ config/
	
clear:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf logs/
	deactivate 2>/dev/null || true
	rm -rf .venv