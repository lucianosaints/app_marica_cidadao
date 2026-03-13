from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import json
import io
import unicodedata
from rest_framework import viewsets, permissions, authentication, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
import tempfile
from fpdf import FPDF

from .models import RelatoZeladoria, CategoriaProblema, WebPushSubscription
from .serializers import (
    RelatoZeladoriaSerializer, 
    UserRegistrationSerializer, 
    CategoriaProblemaSerializer
)
from .ai_service import analisar_imagem_problema

def normalizar_texto(texto):
    """
    Remove acentos e caracteres especiais para garantir compatibilidade com fontes PDF padrão (Latin-1).
    """
    if not texto:
        return ""
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return texto_sem_acento.encode('ascii', 'ignore').decode('ascii')

@method_decorator(csrf_exempt, name='dispatch')
class CustomObtainAuthToken(ObtainAuthToken):
    authentication_classes = []  # Evita CSRF check
    def post(self, request, *args, **kwargs):
        username_input = request.data.get('username', '')
        if username_input:
            username_input = username_input.strip()
            
        password = request.data.get('password', '')
        
        print(f"--- TENTATIVA DE LOGIN --- Usuário: '{username_input}' ---")

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
    Serve o arquivo index.html do frontend com headers que forçam a atualização (Bypass Cache).
    """
    index_path = os.path.join(settings.BASE_DIR, 'frontend_simples', 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        response = HttpResponse(content, content_type='text/html')
        # Força o navegador a sempre perguntar ao servidor se o arquivo mudou
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except FileNotFoundError:
        return HttpResponse("Frontend index.html não encontrado.", status=404)

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

class APILogoutView(APIView):
    """
    Invalida o token do usuário no servidor (Logout real).
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request):
        try:
            # Deleta o token associado ao usuário
            request.user.auth_token.delete()
            return Response({"success": "Sessão encerrada com sucesso no servidor."}, status=200)
        except Exception as e:
            return Response({"error": f"Erro ao encerrar sessão: {str(e)}"}, status=500)

class PublicRelatosView(APIView):
    """
    Endpoint público para transparência social.
    Retorna dados anônimos dos relatos para exibir no mapa da cidade.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        relatos = RelatoZeladoria.objects.all().select_related('categoria')
        data = []
        for r in relatos:
            data.append({
                "id": r.id,
                "categoria_nome": r.categoria.nome,
                "categoria_emoji": r.categoria.emoji,
                "status_display": r.get_status_atual_display(),
                "bairro": r.bairro,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "criado_em": r.criado_em.strftime('%d/%m/%Y'),
                "prioridade": r.prioridade
            })
        return Response(data)

@method_decorator(staff_member_required, name='dispatch')
class DashboardAdminView(TemplateView):
    template_name = 'admin/dashboard_stats.html'

    def get_context_data(self, **kwargs):
        from .utils import get_dashboard_stats
        context = super().get_context_data(**kwargs)
        
        bairro_selecionado = self.request.GET.get('bairro', '')
        
        # Obtém as estatísticas consolidadas via utilitário
        stats = get_dashboard_stats(bairro_selecionado)
        context.update(stats)
        
        return context

class ExportarRelatorioPDFView(APIView):
    """
    Gera um relatório PDF profissional para gestão pública.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            # 1. Coleta de Dados
            total = RelatoZeladoria.objects.count()
            resolvidos = RelatoZeladoria.objects.filter(status_atual='resolvido').count()
            pendentes = RelatoZeladoria.objects.filter(status_atual='recebido').count()
            relatos_recentes = RelatoZeladoria.objects.select_related('categoria').order_by('-criado_em')[:20]

            # 2. Configuração do PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, normalizar_texto("PREFEITURA DE MARICA"), ln=True, align="C")
            pdf.set_font("helvetica", "", 12)
            pdf.cell(0, 10, normalizar_texto("Sistema Marica Cidadao - Relatorio de Gestao Urbana"), ln=True, align="C")
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(10)

            # Seção 1: Resumo Executivo
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, normalizar_texto("1. Resumo Executivo"), ln=True)
            pdf.set_font("helvetica", "", 11)
            pdf.cell(0, 8, normalizar_texto(f"- Total de Ocorrencias Registradas: {total}"), ln=True)
            pdf.cell(0, 8, normalizar_texto(f"- Ocorrencias Solucionadas: {resolvidos}"), ln=True)
            pdf.cell(0, 8, normalizar_texto(f"- Ocorrencias em Aberto: {pendentes}"), ln=True)
            pdf.ln(10)

            # Seção 2: Tabela de Ocorrências Recentes
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, normalizar_texto("2. Ultimas 20 Ocorrencias"), ln=True)
            pdf.ln(5)

            # Cabeçalho da Tabela
            pdf.set_font("helvetica", "B", 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(20, 10, normalizar_texto("ID"), 1, 0, "C", True)
            pdf.cell(60, 10, normalizar_texto("Categoria"), 1, 0, "C", True)
            pdf.cell(40, 10, normalizar_texto("Status"), 1, 0, "C", True)
            pdf.cell(40, 10, normalizar_texto("Data"), 1, 0, "C", True)
            pdf.cell(30, 10, normalizar_texto("Prioridade"), 1, 1, "C", True)

            # Dados da Tabela
            pdf.set_font("helvetica", "", 9)
            for r in relatos_recentes:
                pdf.cell(20, 8, normalizar_texto(f"#{r.id}"), 1, 0, "C")
                nome_cat = r.categoria.nome[:30] if r.categoria else "Sem categoria"
                pdf.cell(60, 8, normalizar_texto(nome_cat), 1, 0, "L")
                pdf.cell(40, 8, normalizar_texto(r.get_status_atual_display()), 1, 0, "C")
                pdf.cell(40, 8, r.criado_em.strftime('%d/%m/%Y'), 1, 0, "C")
                prio = r.prioridade or "Normal"
                pdf.cell(30, 8, normalizar_texto(str(prio)), 1, 1, "C")

            # Rodapé
            pdf.ln(20)
            pdf.set_font("helvetica", "I", 8)
            data_geracao = timezone.now().strftime('%d/%m/%Y as %H:%M:%S')
            pdf.cell(0, 10, normalizar_texto(f"Relatorio gerado em {data_geracao} por sistema automatizado."), 0, 0, "C")

            # 3. Retorno do Arquivo
            # O fpdf2 retorna um bytearray(). O Django pode convertê-lo incorretamente.
            # Garantimos que seja um objeto 'bytes' nativo.
            pdf_content = bytes(pdf.output())
            
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_marica_gestao.pdf"'
            response['Content-Length'] = len(pdf_content)
            return response
            
        except Exception as e:
            import traceback
            print("=== ERRO NA GERAÇÃO DO PDF ===")
            print(traceback.format_exc())
            return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)


class WebPushSubscribeView(APIView):
    """
    Recebe a inscrição WebPush do frontend (PWA) e salva no banco de dados.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request):
        subscription_info = request.data
        
        endpoint = subscription_info.get('endpoint')
        keys = subscription_info.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        if not endpoint or not p256dh or not auth:
            return Response(
                {"error": "Inscrição inválida. 'endpoint', 'p256dh' e 'auth' são obrigatórios."},
                status=400
            )

        # Usar update_or_create para evitar endpoints duplicados e atualizar caso a key mude
        sub, created = WebPushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': p256dh,
                'auth': auth
            }
        )

        acao = "criada" if created else "atualizada"
        print(f"--- INSCRIÇÃO WEBPUSH {acao.upper()} para {request.user.username} ---")
        return Response({"status": f"Inscrição {acao} com sucesso!"}, status=200)

class VapidPublicKeyView(APIView):
    """
    Retorna a chave VAPID pública para o Service Worker do Frontend.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        # Lê a chave diretamente do settings (vamos carregar do decouple)
        vapid_pub = getattr(settings, 'VAPID_PUBLIC_KEY', None)
        if not vapid_pub:
            return Response({"error": "VAPID key não configurada no servidor."}, status=500)
        return Response({"public_key": vapid_pub}, status=200)