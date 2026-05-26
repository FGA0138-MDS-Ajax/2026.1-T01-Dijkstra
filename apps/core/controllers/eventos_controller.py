import json
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.core.services.eventos_service import EventosService

@method_decorator(csrf_exempt, name='dispatch')
class EventosController(View):
    """Controller para gerenciar requisições de Eventos."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EventosService()

    def get(self, request: HttpRequest, evento_id: int = None) -> JsonResponse:
        """Lista todos os eventos ou um evento específico."""
        if evento_id:
            evento = self.service.buscar_evento(evento_id)
            if not evento:
                return JsonResponse({'error': 'Evento não encontrado'}, status=404)
            return JsonResponse(self._serialize_evento(evento))
        
        eventos = self.service.listar_eventos()
        return JsonResponse([self._serialize_evento(e) for e in eventos], safe=False)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Cria um novo evento."""
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                evento = self.service.criar_evento(data)
            else:
                data = request.POST.dict()
                if request.FILES.get('imagem'):
                    data['imagem'] = request.FILES['imagem']
                evento = self.service.criar_evento(data)
                
            return JsonResponse(self._serialize_evento(evento), status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def put(self, request: HttpRequest, evento_id: int) -> JsonResponse:
        """Atualiza um evento existente."""
        try:
            data = json.loads(request.body)
            evento = self.service.atualizar_evento(evento_id, data)
            if not evento:
                return JsonResponse({'error': 'Evento não encontrado'}, status=404)
            return JsonResponse(self._serialize_evento(evento))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def delete(self, request: HttpRequest, evento_id: int) -> JsonResponse:
        """Deleta um evento."""
        success = self.service.excluir_evento(evento_id)
        if not success:
            return JsonResponse({'error': 'Evento não encontrado'}, status=404)
        return JsonResponse({'message': 'Evento deletado com sucesso'}, status=204)

    def _serialize_evento(self, evento) -> dict:
        """Helper para serializar o objeto Evento para dicionário."""
        def format_field(field):
            if hasattr(field, 'isoformat'):
                return field.isoformat()
            return field

        return {
            'id': evento.id,
            'nome': evento.nome,
            'data': format_field(evento.data),
            'horario': format_field(evento.horario),
            'local': evento.local,
            'organizador': evento.organizador,
            'descricao': evento.descricao,
            'capacidade': evento.capacidade,
            'criado_em': format_field(evento.criado_em),
            'atualizado_em': format_field(evento.atualizado_em),
            'imagem': evento.imagem.url if evento.imagem and hasattr(evento.imagem, 'url') else None,
        }
