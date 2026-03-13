from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RelatoZeladoriaViewSet, RegisterUserView, CategoriaProblemaViewSet, APIAnalisarFoto, DashboardAdminView, APILogoutView, PublicRelatosView, ExportarRelatorioPDFView, WebPushSubscribeView, VapidPublicKeyView

router = DefaultRouter()
# Cria as rotas: GET /api/relatos/ e POST /api/relatos/
router.register(r'relatos', RelatoZeladoriaViewSet, basename='relato')
router.register(r'categorias', CategoriaProblemaViewSet, basename='categoria')

urlpatterns = [
    path('cadastro/', RegisterUserView.as_view(), name='registrar_usuario'),
    path('logout/', APILogoutView.as_view(), name='api_logout'),
    path('analisar-foto/', APIAnalisarFoto.as_view(), name='analisar_foto'),
    path('dashboard-estatisticas/', DashboardAdminView.as_view(), name='admin_dashboard_stats'),
    path('exportar-pdf/', ExportarRelatorioPDFView.as_view(), name='exportar_pdf_gestao'),
    path('public/relatos/', PublicRelatosView.as_view(), name='public_relatos'),
    path('webpush/inscrever/', WebPushSubscribeView.as_view(), name='webpush_subscribe'),
    path('webpush/vapid-public-key/', VapidPublicKeyView.as_view(), name='vapid_public_key'),
    path('', include(router.urls)),
]