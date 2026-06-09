from apps.security.models.usuario_models import Usuario
from apps.security.repositories.usuarios_repositories import UsuarioRepository

class UsuarioService:
    def __init__(self):
        self.repository = UsuarioRepository()