from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
from rest_framework import viewsets, permissions, authentication, generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import RelatoZeladoria, CategoriaProblema
from .serializers import (
    RelatoZeladoriaSerializer, 
    UserRegistrationSerializer, 
    CategoriaProblemaSerializer
)
from .ai_service import analisar_imagem_problema
import tempfile


from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

@method_decorator(csrf_exempt, name='dispatch')
class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = []  # Evita CSRF check
    def post(self, request, *args, **kwargs):
        username_input = request.data.get('username')
        password = request.data.get('password')

        # 1. Tenta autenticar pelo username (padrão)
        user = authenticate(username=username_input, password=password)

        # 2. Se falhar, tenta buscar por email (pode haver mais de um)
        if user is None:
            users_with_email = User.objects.filter(email=username_input)
            for u in users_with_email:
                user = authenticate(username=u.username, password=password)
                if user:
                    break

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username
            })
        
        return Response({'error': 'Cidadão não encontrado ou senha incorreta.'}, status=400)

class CategoriaProblemaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lista as categorias disponíveis para o cidadão selecionar no formulário.
    """
    queryset = CategoriaProblema.objects.all()
    serializer_class = CategoriaProblemaSerializer
    permission_classes = [permissions.AllowAny] # Aberto para o formulário de cadastro/relato funcionar sem travas
    authentication_classes = [] # Evita problemas de CSRF/Token inicial

@method_decorator(csrf_exempt, name='dispatch')
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.none()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Evita CSRF check
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            import traceback
            print("=== ERRO CRÍTICO NO CADASTRO ===")
            print(traceback.format_exc())
            return Response({"detail": str(e)}, status=500)

class RelatoZeladoriaViewSet(viewsets.ModelViewSet):
    serializer_class = RelatoZeladoriaSerializer
    authentication_classes = [authentication.TokenAuthentication]
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

@csrf_exempt
def frontend_view(request):
    """
    Serve o arquivo index.html do frontend sem usar o motor de templates do Django,
    evitando conflitos com a sintaxe JSX (chaves duplas).
    """
    index_path = os.path.join(settings.BASE_DIR, 'frontend_simples', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Frontend index.html não encontrado.", status=404)

from rest_framework.views import APIView
class APIAnalisarFoto(APIView):
    """
    Recebe uma foto e retorna o palpite da IA sobre a categoria.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        foto = request.FILES.get('foto_problema')
        if not foto:
            return Response({"error": "Nenhuma foto enviada."}, status=400)

        # Salva temporariamente para processar
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", mode='wb') as tmp:
            for chunk in foto.chunks():
                tmp.write(chunk)
            temp_path = tmp.name

        try:
            resultado = analisar_imagem_problema(temp_path)
            # Remove o arquivo temporário
            os.remove(temp_path)
            return Response(resultado)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({"error": str(e)}, status=500)

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

@method_decorator(staff_member_required, name='dispatch')
class DashboardAdminView(TemplateView):
    template_name = 'admin/dashboard_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Estatísticas de Status
        status_stats = RelatoZeladoria.objects.values('status_atual').annotate(total=Count('id'))
        
        # 2. Estatísticas de Categoria
        categoria_stats = RelatoZeladoria.objects.values('categoria__nome').annotate(total=Count('id')).order_by('-total')
        
        # 3. Evolução dos últimos 30 dias
        trinta_dias_atras = timezone.now() - timedelta(days=30)
        evolucao_stats = RelatoZeladoria.objects.filter(
            criado_em__gte=trinta_dias_atras
        ).annotate(
            data=TruncDate('criado_em')
        ).values('data').annotate(
            total=Count('id')
        ).order_by('data')

        # 4. Formatação para o Chart.js
        context['status_stats_json'] = list(status_stats)
        context['categoria_stats_json'] = list(categoria_stats)
        context['evolucao_stats_json'] = [
            {'data': item['data'].strftime('%d/%m'), 'total': item['total']} 
            for item in evolucao_stats
        ]
        
        # 5. KPIs (Indicadores Chave)
        context['total_relatos'] = RelatoZeladoria.objects.count()
        context['resolvidos'] = RelatoZeladoria.objects.filter(status_atual='resolvido').count()
        context['pendentes'] = RelatoZeladoria.objects.filter(status_atual='recebido').count()
        context['em_andamento'] = RelatoZeladoria.objects.filter(status_atual='em_progresso').count()
        
        return context