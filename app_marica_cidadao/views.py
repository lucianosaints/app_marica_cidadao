from rest_framework import viewsets, permissions, authentication
from rest_framework.parsers import MultiPartParser, FormParser
from .models import RelatoZeladoria
from .serializers import RelatoZeladoriaSerializer

class RelatoZeladoriaViewSet(viewsets.ModelViewSet):
    serializer_class = RelatoZeladoriaSerializer
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    # Importante: Permite receber arquivos de imagem (FormData do React)
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Garante que o cidadão só consiga ver a lista dos SEUS próprios chamados,
        e não os chamados de outros moradores.
        """
        user = self.request.user
        # Se for um funcionário da prefeitura, poderia ver todos:
        if user.is_staff:
            return RelatoZeladoria.objects.all()
        # Se for cidadão comum, vê apenas os dele:
        return RelatoZeladoria.objects.filter(cidadao=user).order_by('-criado_em')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("=== ERROS DE VALIDAÇÃO DO SERIALIZER ===")
            print(serializer.errors)
        return super().create(request, *args, **kwargs)