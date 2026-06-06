# Débito Técnico — apps.core

## DT-002 · `except Exception` expondo detalhes internos
**Arquivo:** `apps/core/controllers/eventos_controller.py` — `post`, `put`
**Impacto:** Segurança — `str(e)` pode vazar stack traces, nomes de tabelas e paths do servidor ao cliente.
**Ação:** Logar a exceção internamente e retornar mensagem genérica ao cliente.

---

## DT-003 · Sem paginação em `listar_eventos`
**Arquivo:** `apps/core/repositories/eventos_repository.py` — `get_all`
**Impacto:** Performance — `list(Evento.objects.all())` carrega todos os registros em memória.
**Ação:** Implementar paginação via `Paginator` ou adotar DRF com `PageNumberPagination`.

---

## DT-004 · Sem validação de dados no `POST` e `PUT`
**Arquivo:** `apps/core/controllers/eventos_controller.py` — `post`, `put`
**Impacto:** Integridade — dados inválidos ou campos inesperados chegam direto ao banco via `create(**data)` e `setattr`.
**Ação:** Implementar camada de validação no service ou adotar serializers do DRF.

---

## DT-006 · `@csrf_exempt` global no controller
**Arquivo:** `apps/core/controllers/eventos_controller.py`
**Impacto:** Segurança — todas as requisições ficam sem proteção CSRF. Aceitável apenas se a autenticação via `apps.security` utilizar tokens e não cookies de sessão.
**Ação:** Verificar o mecanismo de autenticação do `apps.security` e remover o `csrf_exempt` se sessões forem utilizadas.
