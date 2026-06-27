from apps.security.models.usuario_models import Usuario

class UsuarioRepository:
    def __init__(self):
        self.model = Usuario

    def create_usuario(self, usuario_data):
        return self.model.objects.create(**usuario_data)
    
    def get_usuario_by_id(self, usuario_id):
        return self.model.objects.get(id=usuario_id)

    def get_all_usuarios(self):
        return self.model.objects.all()
    
    def get_organizadores_usuarios(self):
        return self.model.objects.filter(tipo='OR')
    
    def update_usuario(self, usuario_id, usuario_data):
        usuario = self.get_usuario_by_id(usuario_id)
        for key, value in usuario_data.items():
            setattr(usuario, key, value)
        usuario.save()
        return usuario

    def delete_usuario(self, usuario_id):
        usuario = self.get_usuario_by_id(usuario_id)
        usuario.delete()