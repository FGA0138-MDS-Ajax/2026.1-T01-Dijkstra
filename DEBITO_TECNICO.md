# Débito Técnico — apps.core

## DT-001 · `gestor` ausente na serialização
**Arquivo:** `apps/core/controllers/eventos_controller.py` — `_serialize_evento`
**Impacto:** Bug — o campo `gestor` existe no model e é persistido, mas nunca é retornado pela API.
**Ação:** Adicionar `"gestor": evento.gestor` no dicionário retornado por `_serialize_evento`.

---

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

## DT-005 · `@staticmethod` instanciado desnecessariamente
**Arquivo:** `apps/core/services/eventos_service.py` — `__init__`
**Impacto:** Design — `EventosRepository()` é instanciado mas todos os seus métodos são estáticos, tornando a instância inútil.
**Ação:** Chamar os métodos diretamente pela classe (`EventosRepository.create(...)`) ou converter os métodos para instância.

---

## DT-006 · `@csrf_exempt` global no controller
**Arquivo:** `apps/core/controllers/eventos_controller.py`
**Impacto:** Segurança — todas as requisições ficam sem proteção CSRF. Aceitável apenas se a autenticação via `apps.security` utilizar tokens e não cookies de sessão.
**Ação:** Verificar o mecanismo de autenticação do `apps.security` e remover o `csrf_exempt` se sessões forem utilizadas.
